# Системы координат course_ackermann

Корень дерева — `base_link`. Каждое преобразование издаёт только `robot_state_publisher`. Фиксированные суставы уходят в `/tf_static` (reliable, transient local). Подвижные — в `/tf` (reliable, volatile) и только после `/joint_states`; для зачёта publisher суставов не запускается.

Единицы СИ. Оси REP-103: x вперёд, y влево, z вверх. Размеры взяты из SDF `course_ackermann`: колесная база `0.80` м, колея `0.62` м, радиус колеса `0.12` м. Сенсоры стоят в `0.28 0 0.38` относительно `base_link`.

`tf2_echo base_link lidar_link`: translation `[0.280, 0.000, 0.380]`, поворот нулевой.

| Сустав | Родитель | Потомок | Тип | Ожидаемое преобразование | Топик | Владелец |
| --- | --- | --- | --- | --- | --- | --- |
| `camera_joint` | `base_link` | `camera_link` | fixed | xyz `0.28 0 0.38`, rpy `0 0 0` | `/tf_static` | `robot_state_publisher` |
| `camera_optical_joint` | `camera_link` | `camera_optical_frame` | fixed | xyz `0 0 0`, rpy `-π/2 0 -π/2` (оптическая ось z вперёд) | `/tf_static` | `robot_state_publisher` |
| `lidar_joint` | `base_link` | `lidar_link` | fixed | xyz `0.28 0 0.38`, rpy `0 0 0` | `/tf_static` | `robot_state_publisher` |
| `imu_joint` | `base_link` | `imu_link` | fixed | xyz `0.28 0 0.38`, rpy `0 0 0` | `/tf_static` | `robot_state_publisher` |
| `front_left_steering_joint` | `base_link` | `front_left_knuckle` | revolute | xyz `0.4 0.31 0`, ось z, предел ±0.55 рад | `/tf` | `robot_state_publisher` |
| `front_right_steering_joint` | `base_link` | `front_right_knuckle` | revolute | xyz `0.4 -0.31 0`, ось z, предел ±0.55 рад | `/tf` | `robot_state_publisher` |
| `front_left_wheel_joint` | `front_left_knuckle` | `front_left_wheel` | continuous | xyz `0 0 0`, ось y | `/tf` | `robot_state_publisher` |
| `front_right_wheel_joint` | `front_right_knuckle` | `front_right_wheel` | continuous | xyz `0 0 0`, ось y | `/tf` | `robot_state_publisher` |
| `rear_left_wheel_joint` | `base_link` | `rear_left_wheel` | continuous | xyz `-0.4 0.31 0`, ось y | `/tf` | `robot_state_publisher` |
| `rear_right_wheel_joint` | `base_link` | `rear_right_wheel` | continuous | xyz `-0.4 -0.31 0`, ось y | `/tf` | `robot_state_publisher` |

Visual и collision заданы отдельно: корпус — коробка `1.05 0.52 0.22` со смещением `z=0.12`, колесо — цилиндр радиуса `wheel_radius`, повёрнутый на π/2 вокруг x, чтобы ось совпала с y.
