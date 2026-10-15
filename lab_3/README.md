# Lab 3 / PR03

Пакет `src/patrol/` — нода с подпиской на `/turtle1/pose` и таймером 0.1 с,
публикующим `geometry_msgs/msg/Twist` в относительный `cmd_vel`.

Артефакты: `evidence/pr03/` (`demo.md`, `tests.txt`, `report.json`).

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
colcon build --symlink-install --packages-select patrol
source install/setup.bash
export ROS_DOMAIN_ID=16
python3 -m pytest src/patrol/test

# терминал A
ros2 launch turtle_bringup sim.launch.py

# терминал B
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Дефект имени: запуск без remap публикует в `/cmd_vel`, turtlesim слушает `/turtle1/cmd_vel`.
