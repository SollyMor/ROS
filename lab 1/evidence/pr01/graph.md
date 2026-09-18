# PR01 · граф turtlesim

Домены опыта: **working = 16**, **broken = 17** (подставьте свою пару).

## Команды окружения

```bash
source /opt/ros/<distro>/setup.bash
export ROS_DOMAIN_ID=16
```

## Стадия 1 · исправный граф (оба участника в домене 16)

### Ноды

```text
# ros2 node list --no-daemon --spin-time 2
# вставьте вывод
```

| Нода | Роль |
|------|------|
| `/turtlesim` | симулятор, публикует позу, слушает cmd_vel |
| `/teleop_turtle` | клавиатура → `/turtle1/cmd_vel` |

### Топики и типы

```text
# ros2 topic list -t
# вставьте вывод
```

Ключевые:

| Топик | Тип | Направление |
|-------|-----|-------------|
| `/turtle1/pose` | `turtlesim/msg/Pose` или `turtlesim_msgs/msg/Pose` | turtlesim → |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | teleop → turtlesim |

### Поза (один раз)

```text
# ros2 topic echo /turtle1/pose --once
# вставьте вывод
```

### Частота `/turtle1/pose`

- Длительность замера: _с_
- Средняя частота: _Гц_ (ориентир ~60–62.5)

```text
# ros2 topic hz /turtle1/pose
# вставьте вывод
```

## Стадия 2 · сбой (teleop и CLI в домене 17, turtlesim в 16)

```text
# ros2 node list --no-daemon --spin-time 2   # DOMAIN=17
# ожидается /teleop_turtle, нет /turtlesim
```

```text
# timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once
# файл: pose-broken.txt
# exit=124
```

## Стадия 3 · восстановление (все снова в домене 16)

```text
# ros2 node list --no-daemon --spin-time 2   # DOMAIN=16
# ожидаются /turtlesim и /teleop_turtle
```

```text
# timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once
# файл: pose-fixed.txt
# exit=0
```

## Сравнение

| | Домен turtlesim | Домен teleop/CLI | Ноды видны | Поза | exit |
|--|-----------------|------------------|------------|------|------|
| до | 16 | 16 | обе | да | 0 |
| сбой | 16 | 17 | только teleop | нет | 124 |
| после | 16 | 16 | обе | да | 0 |

## Почему перезапускали teleop

`ROS_DOMAIN_ID` читается при старте процесса. Смена `export` в оболочке не переносит уже запущенную ноду в другой домен. Симулятор и установку ROS менять не нужно: достаточно перезапустить участника, который должен сменить область обнаружения.
