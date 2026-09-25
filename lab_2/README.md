# Lab 2 / PR02

Workspace и артефакты — в корне репозитория (как в задании):

- `src/turtle_bringup/` — пакет с `launch/sim.launch.py`
- `evidence/pr02/` — логи сборки, `commands.md`, `types.md`, `report.json`

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```
