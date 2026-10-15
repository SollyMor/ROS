# PR03 — patrol: поза, таймер, remap

Среда: ROS 2 Jazzy, `ROS_DOMAIN_ID=16`, workspace с `turtle_bringup` (ПР02) и `patrol`.

Тип позы: `ros2 topic type /turtle1/pose` → `turtlesim/msg/Pose`.

## Роли `init`, `spin`, callback и `Ctrl+C`

- **`rclpy.init`** — один раз поднимает клиентскую библиотеку ROS 2 в процессе (контекст, аргументы). Без него нельзя создавать ноды.
- **`rclpy.spin(node)`** — цикл обработки: доставляет сообщения в subscription-callback и срабатывания таймера. Пока крутится `spin`, нода «жива».
- **callback подписки** (`_on_pose`) — только сохраняет последнее `Pose` в поле объекта; тяжёлую логику и публикацию сюда не кладём.
- **callback таймера** (`_on_timer`, 0.1 с) — вызывает чистую функцию `twist_from_pose` и публикует `Twist` в относительный топик `cmd_vel`.
- **`Ctrl+C`** — прерывает `spin` (`KeyboardInterrupt`). Исчезновение процесса **не** равно нулевой команде: turtlesim продолжает применять **последний** полученный `Twist`, пока не придёт новая команда или не будет закрыт сам симулятор. После остановки ноды нужно дождаться остановки черепахи (или явно опубликовать нулевой `Twist`).

## 1 · Собрать

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
colcon build --symlink-install --packages-select patrol
source install/setup.bash
export ROS_DOMAIN_ID=16
python3 -m pytest src/patrol/test
```

В одном терминале:

```bash
ros2 launch turtle_bringup sim.launch.py
# или: ros2 run turtlesim turtlesim_node
```

В другом — исправный запуск с remap:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Нода `/patrol` подписана на `/turtle1/pose`; после первой позы публикует `linear.x=0.5`, `angular.z=0.3`.

## 2 · Сломать (относительное имя без remap)

```bash
ros2 run patrol patrol
```

Издатель уходит в `/cmd_vel` (относительное `cmd_vel` у ноды в `/`), а turtlesim слушает `/turtle1/cmd_vel`.

`ros2 topic info /cmd_vel --verbose`:

- Publisher count: **1** (`patrol`)
- Subscription count: **0**

`ros2 topic info /turtle1/cmd_vel --verbose`:

- Publisher count: **0**
- Subscription count: **1** (`turtlesim`)

Поза не менялась:

```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

## 3 · Доказать (remap + поза + частота)

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

После remap на `/turtle1/cmd_vel`: Publisher count **1** (`patrol`) и Subscription count **1** (`turtlesim`). Поза меняется, скорости совпадают с командой:

```
x: 7.089456081390381
y: 6.596009254455566
theta: 1.1904000043869019
linear_velocity: 0.5
angular_velocity: 0.30000001192092896
```

Частота команды за ~10 с (`ros2 topic hz /turtle1/cmd_vel`):

```
average rate: 10.001
	min: 0.099s max: 0.101s std dev: 0.00051s window: 87
```

≈ **10 Hz**, как у таймера 0.1 с.

### Почему «правильный тип» недостаточен

Тип `geometry_msgs/msg/Twist` совпадает, но DDS доставляет сообщение только при совпадении **полного имени** топика. `/cmd_vel` и `/turtle1/cmd_vel` — разные endpoints: discovery показывает publisher, matching subscription у turtlesim на другом имени.
