# PR01 · граф turtlesim

Домены: working = **16**, broken = **17**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
```

## 1 · Исправный граф (домен 16)

### Ноды

```text
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
/turtlesim
```

| Нода | Роль |
|------|------|
| `/turtlesim` | симулятор: публикует `/turtle1/pose`, слушает `/turtle1/cmd_vel` |
| `/teleop_turtle` | клавиатура → `/turtle1/cmd_vel` |

### Топики

```text
$ ros2 topic list -t
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```

`POSE_TYPE=turtlesim/msg/Pose`

### Поза

```text
$ ros2 topic echo /turtle1/pose --once
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
```

### Частота `/turtle1/pose`

Длительность ≈ 12 с. Средняя частота ≈ **62.5 Гц**.

```text
$ ros2 topic hz /turtle1/pose
average rate: 62.437
	min: 0.015s max: 0.017s std dev: 0.00054s window: 64
average rate: 62.495
	min: 0.015s max: 0.017s std dev: 0.00051s window: 631
```

## 2 · Сбой (teleop и CLI в домене 17, turtlesim в 16)

```text
$ export ROS_DOMAIN_ID=17
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
```

```text
$ timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once
# → evidence/pr01/pose-broken.txt
exit=124
```

Поза не приходит. Виден только `/teleop_turtle`, `/turtlesim` в домене 17 не обнаружен.

## 3 · Восстановление (все в домене 16)

```text
$ export ROS_DOMAIN_ID=16
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
/turtlesim
```

```text
$ timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once
# → evidence/pr01/pose-fixed.txt
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
exit=0
```

## Сравнение

| | Домен turtlesim | Домен teleop/CLI | Ноды | Поза | exit |
|--|-----------------|------------------|------|------|------|
| до | 16 | 16 | обе | да | 0 |
| сбой | 16 | 17 | только teleop | нет | 124 |
| после | 16 | 16 | обе | да | 0 |

## Почему перезапускали teleop

`ROS_DOMAIN_ID` читается при старте процесса. `export` в оболочке не переносит уже запущенную ноду в другой домен. Симулятор и установку ROS менять не нужно — достаточно перезапустить участника, который меняет область обнаружения.
