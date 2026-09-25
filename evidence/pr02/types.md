# PR02 — типы сообщений

## Основные топики

| Топик | Тип | Назначение |
|-------|-----|------------|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | команды скорости черепахе |
| `/turtle1/pose` | `turtlesim/msg/Pose` | текущая поза черепахи (Jazzy) |

Неверный топик из эксперимента «сломать»: `/cmd_vel` (тот же `Twist`, но без подписчика turtlesim).

## Поля `geometry_msgs/msg/Twist`

- `linear.x / y / z` — линейная скорость по осям (м/с). В turtlesim движение в плоскости задаётся в основном `linear.x` (вперёд/назад).
- `angular.x / y / z` — угловая скорость (рад/с). В turtlesim поворот — `angular.z`.

## Поля `turtlesim/msg/Pose` (Jazzy)

- `x`, `y` — положение на поле симулятора
- `theta` — ориентация (рад)
- `linear_velocity`, `angular_velocity` — текущие скорости

> В Lyrical тип позы может быть `turtlesim_msgs/msg/Pose`. У нас `ros2 topic type /turtle1/pose` → `turtlesim/msg/Pose`.
