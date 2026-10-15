# ROS course labs

## PR04 — patrol parameters

Параметры `linear_speed`, `turn_rate`, `publish_hz` управляют командой и таймером.
Недопустимый `publish_hz` (0, отрицательный, NaN) отклоняется; частота и поток сохраняются.

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
colcon build --symlink-install --packages-select patrol
source install/setup.bash
export ROS_DOMAIN_ID=16
python3 -m pytest src/patrol/test
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
ros2 param set /patrol publish_hz 5.0
ros2 param set /patrol publish_hz 0.0
```

Артефакты: `evidence/pr04/`.

---

## PR03 — patrol node (pose + cmd_vel)

Пакет `src/patrol`: подписка на `/turtle1/pose`, таймер 0.1 с, публикация `Twist`
в относительный `cmd_vel`. Нужен remap на `/turtle1/cmd_vel`.

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
colcon build --symlink-install --packages-select patrol
source install/setup.bash
export ROS_DOMAIN_ID=16
python3 -m pytest src/patrol/test
ros2 launch turtle_bringup sim.launch.py
# другой терминал:
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Артефакты: `evidence/pr03/`. Checker:

```bash
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

---

## PR02 — turtle_bringup launch

Пакет `src/turtle_bringup` запускает готовый `turtlesim` через `sim.launch.py`.

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
colcon build --symlink-install --packages-select turtle_bringup
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```

Движение (другой терминал, тот же domain):

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Артефакты: `evidence/pr02/`. Проверка синтаксиса launch:

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
```

---

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
