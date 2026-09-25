# PR01 — turtlesim и ROS_DOMAIN_ID

## Подготовка (три терминала)

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
```

В терминале C из корня репозитория:

```bash
mkdir -p evidence/pr01
ros2 doctor --report > evidence/pr01/doctor.txt 2>&1
```

## 1 · Собрать

**A:** `ros2 run turtlesim turtlesim_node`  
**B:** `ros2 run turtlesim turtle_teleop_key`  

**C:**

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
POSE_TYPE=$(ros2 topic type /turtle1/pose)
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose   # ≥10 с, Ctrl+C
```

Записать вывод в `evidence/pr01/graph.md`.

## 2 · Сломать

A остаётся в домене 16. B и C:

```bash
export ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key   # только B
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```

Ожидание: `/teleop_turtle` без `/turtlesim`, `exit=124`.

## 3 · Доказать

B и C снова `ROS_DOMAIN_ID=16`, перезапуск teleop:

```bash
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
printf 'exit=%s\n' "$?"
```

Ожидание: обе ноды, поза, `exit=0`.

## 4 · Оформить и проверить

Заполнить `evidence/pr01/environment.json` и `report.json`.

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 scripts/check_pr01.py
```
