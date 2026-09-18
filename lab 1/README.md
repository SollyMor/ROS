# Lab 1 · PR01 — turtlesim и домены

Запуск готовой системы turtlesim, описание графа и проверка изоляции через `ROS_DOMAIN_ID`.

## Что сдать

| Файл | Смысл |
|------|--------|
| `evidence/pr01/doctor.txt` | вывод `ros2 doctor --report` |
| `evidence/pr01/graph.md` | ноды, топики, частота, сравнение доменов |
| `evidence/pr01/environment.json` | ОС, ROS, RMW, домены |
| `evidence/pr01/pose-broken.txt` | echo позы в чужом домене (таймаут) |
| `evidence/pr01/pose-fixed.txt` | echo позы после возврата в исходный домен |
| `report.json` | заявления и список выполненных проверок |

## Подготовка терминалов

Три Bash-терминала (A — симулятор, B — teleop, C — наблюдение). В каждом:

```bash
source /opt/ros/jazzy/setup.bash   # Ubuntu 24.04
# source /opt/ros/lyrical/setup.bash  # Ubuntu 26.04
export ROS_DOMAIN_ID=16            # своя пара доменов: здесь 16 и 17
```

В терминале C, из корня репозитория:

```bash
mkdir -p "lab 1/evidence/pr01"
ros2 doctor --report > "lab 1/evidence/pr01/doctor.txt" 2>&1
```

## 1 · Собрать (исправный граф)

**A**

```bash
ros2 run turtlesim turtlesim_node
```

**B**

```bash
ros2 run turtlesim turtle_teleop_key
```

Стрелки при фокусе в B двигают черепаху.

**C**

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose
POSE_TYPE=$(ros2 topic type /turtle1/pose)
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose   # ≥10 с, затем Ctrl+C
```

Запишите вывод и частоту в `evidence/pr01/graph.md`.  
Тип позы: Jazzy — `turtlesim/msg/Pose`, Lyrical — `turtlesim_msgs/msg/Pose`.

## 2 · Сломать (другой домен)

Симулятор A остаётся в домене 16. В B:

```bash
# Ctrl+C teleop
export ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key
```

В C:

```bash
export ROS_DOMAIN_ID=17
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > "lab 1/evidence/pr01/pose-broken.txt" 2>&1
printf 'exit=%s\n' "$?"
```

Ожидается: есть `/teleop_turtle`, нет `/turtlesim`, поза не приходит, `exit=124`.

## 3 · Доказать (вернуть домен)

В B снова `ROS_DOMAIN_ID=16` и перезапуск teleop. В C:

```bash
export ROS_DOMAIN_ID=16
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > "lab 1/evidence/pr01/pose-fixed.txt" 2>&1
printf 'exit=%s\n' "$?"
```

Ожидается: обе ноды, поза приходит, `exit=0`. Добавьте сравнение «до / сбой / после» в `graph.md`.

Почему перезапускали teleop, а не turtlesim: `export ROS_DOMAIN_ID` действует на новые процессы; уже запущенная нода домен не меняет.

## 4 · Оформить

1. Заполните `environment.json` (способ запуска, ОС, ROS, Gazebo, RMW, домены).
2. Заполните `report.json` (`public_tests_passed`, `defect_reproduced`, `defect_fixed`, список `tests`).
3. Проверка JSON:

```bash
python3 -m json.tool "lab 1/evidence/pr01/environment.json" > /dev/null
python3 -m json.tool "lab 1/report.json" > /dev/null
```

Если в репозитории есть course kit:

```bash
python3 .course-kit/v1/tools/check_practice.py PR01 --submission "lab 1"
```

## Заметки

- `export` не перенастраивает уже работающую ноду.
- Перед опытом остановите старые talker/listener и turtlesim (`Ctrl+C`).
- Evidence коммитьте отдельно от README/CI, когда опыт реально выполнен.
