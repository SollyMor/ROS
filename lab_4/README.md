# Lab 4 / PR04

Параметры ноды `patrol`: `linear_speed`, `turn_rate`, `publish_hz`.
Недопустимая частота отклоняется без разрушения активного состояния.

Артефакты: `evidence/pr04/` (`parameters.md`, `tests.txt`, `report.json`).

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
colcon build --symlink-install --packages-select patrol
source install/setup.bash
export ROS_DOMAIN_ID=16
python3 -m pytest src/patrol/test

ros2 run turtlesim turtlesim_node
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel

ros2 param set /patrol publish_hz 5.0
ros2 param set /patrol publish_hz 0.0   # rejected; value stays 5.0
```
