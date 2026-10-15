# PR04 — параметры patrol

Среда: ROS 2 Jazzy, `ROS_DOMAIN_ID=16`, нода с remap:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 run turtlesim turtlesim_node
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Параметры по умолчанию: `linear_speed=0.5`, `turn_rate=0.3`, `publish_hz=10.0`.
Допустимые диапазоны: скорость 0–1 м/с, поворот −1–1 рад/с, частота 1–30 Гц.

## Обычное изменение 10 → 5 Гц

```bash
ros2 param set /patrol publish_hz 5.0
# Set parameter successful
ros2 param get /patrol publish_hz
# Double value is: 5.0
ros2 topic hz /turtle1/cmd_vel
```

```
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00065s window: 29
```

Таймер пересоздан с периодом `1/5 = 0.2` с; прежний таймер остановлен.

## Сломать: частота 0 без проверки

Если проверку `publish_hz` временно отключить, период считается как `1/publish_hz`.
Для нуля это даёт конкретный отказ:

```bash
python3 -c 'from patrol.command import timer_period; timer_period(0.0)'
# ZeroDivisionError: float division by zero
```

Нода падает (или callback параметров роняет процесс) при попытке пересоздать таймер — активное состояние разрушается.

## Доказать: ноль отклонён, частота сохранена

С включённой проверкой:

```bash
ros2 param set /patrol publish_hz 0.0
# Setting parameter failed: publish_hz must be in [1.0, 30.0] Hz
ros2 param get /patrol publish_hz
# Double value is: 5.0
```

Значение осталось **5.0**, поток команд не сломан.

Отрицательное значение:

```bash
ros2 param set /patrol publish_hz -1.0
# Setting parameter failed: publish_hz must be in [1.0, 30.0] Hz
```

NaN через Parameter API:

```
successful=False reason='publish_hz must be a finite number'
publish_hz remains 5.0
```

Чистые тесты (`validate_publish_hz` / `timer_period`) покрывают 5 Гц, 0, отрицательное и NaN — см. `tests.txt`.

## Сервис `/clear` и action `/turtle1/rotate_absolute`

```bash
ros2 service call /clear std_srvs/srv/Empty
# response: std_srvs.srv.Empty_Response()

ros2 action list -t
# /turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
```

Запрос сервиса — разовый вызов с ответом (здесь пустой `Empty`). Цель action — долгоживущая задача с обратной связью и возможностью отмены, а не один синхронный ответ.
