# PR02 — Linux commands, launch, CLI

## 1. Три Linux-команды из лабораторной

### `pwd`
- **Команда:** `pwd`
- **Зачем:** показать текущую директорию (корень репозитория / workspace).
- **Результат:** `/home/soffa/Desktop/ROSS/ROS`

### `mkdir -p`
- **Команда:** `mkdir -p src evidence/pr02`
- **Зачем:** создать дерево каталогов для пакетов и артефактов, не падая, если они уже есть.
- **Результат:** появились `src/` и `evidence/pr02/`.

### `tee`
- **Команда:** `colcon build ... 2>&1 | tee evidence/pr02/build.txt`
- **Зачем:** одновременно показать лог сборки в терминале и сохранить его в файл.
- **Результат:** файл `evidence/pr02/build.txt` с успешным `Finished <<< turtle_bringup`.

### `>` vs `|`
- `>` перенаправляет stdout в файл (перезаписывает файл).
- `|` передаёт stdout одной команды на stdin другой (конвейер), без обязательной записи на диск.

### `source` vs запуск новой программы
- `source setup.bash` выполняет скрипт **в текущем** shell: переменные (`PATH`, `ROS_DISTRO`, `AMENT_PREFIX_PATH`) остаются в сессии.
- Запуск `./setup.bash` или `bash setup.bash` идёт в **дочернем** процессе: после выхода окружение родительского терминала не меняется, `ros2` из workspace не появится.

---

## 2. Launch и граф

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 pkg prefix turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
ros2 launch turtle_bringup sim.launch.py
```

Проверка ноды (другой терминал, тот же domain):

```bash
ros2 node list --no-daemon --spin-time 2
# /turtlesim
```

Остановка: `Ctrl+C` — окно turtlesim закрывается.

---

## 3. CLI: команда → движение

Ожидаемое направление: вперёд (`linear.x = 1.0`) и поворот влево (`angular.z = 0.5`).

**До:**
```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
```

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

**После:**
```
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
```

Одной публикации недостаточно для бесконечного движения — без новых команд turtlesim останавливается.

---

## 4. Сломать имя топика и доказать исправление

### До / ошибка (неверный топик `/cmd_vel`)

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

`ros2 topic info /cmd_vel --verbose`:
- Publisher count: **1** (`_ros2cli_...`)
- Subscription count: **0**

`ros2 topic info /turtle1/cmd_vel --verbose`:
- Publisher count: **0**
- Subscription count: **1** (`turtlesim`)

Поза не менялась (`x≈6.51`, `y≈5.80`) — publisher виден (discovery), но доставки подписчику turtlesim нет.

### После (исправленное имя `/turtle1/cmd_vel`)

Тот же `Twist`, только имя топика заменено на `/turtle1/cmd_vel`. Черепаха поехала:

```
x: 7.212432861328125
y: 8.635802268981934
theta: 2.1440000534057617
linear_velocity: 1.0
angular_velocity: 0.5
```

После `Ctrl+C` на publisher скорости обнулились, движение прекратилось.

### Почему «правильный тип» недостаточно
Тип `geometry_msgs/msg/Twist` совпадает, но DDS/ROS доставляет сообщение только при **совпадении полного имени топика**. `/cmd_vel` и `/turtle1/cmd_vel` — разные endpoints: discovery показывает publisher, но matching subscription у turtlesim на другом имени, поэтому доставки (delivery) нет.
