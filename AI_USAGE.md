# Декларация использования ИИ

## PR02

```yaml
practice_id: PR02
ai_used: true
model: Composer (Cursor Agent)
tool: Cursor IDE
help: packaging turtle_bringup, launch file, evidence docs, CI workflow
verification: colcon build; ros2 launch turtle_bringup sim.launch.py; ros2 topic pub/echo; python3 -m py_compile
```

## PR03

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Composer (Cursor Agent)
- Среда или интерфейс агента: Cursor IDE
- Затронутые компоненты: пакет `src/patrol`, чистая функция `twist_from_pose`, unit-тесты, `evidence/pr03`, workflow `pr03.yml`, `AI_USAGE.md`
- Характер помощи: создание ноды patrol (подписка, таймер, относительный `cmd_vel`), оформление evidence и CI по course-kit
- Как результат был проверен независимо: `colcon build --packages-select patrol`; `python3 -m pytest src/patrol/test`; живой прогон turtlesim без/с remap; `ros2 topic hz /turtle1/cmd_vel`; `check_practice.py PR03`

## PR04

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Composer (Cursor Agent)
- Среда или интерфейс агента: Cursor IDE
- Затронутые компоненты: параметры `patrol`, валидация `publish_hz`/`linear_speed`/`turn_rate`, пересоздание таймера, тесты, `evidence/pr04`, workflow `pr04.yml`
- Характер помощи: параметризация ноды, отклонение недопустимой частоты, оформление evidence и CI
- Как результат был проверен независимо: `python3 -m pytest src/patrol/test`; `ros2 param set` 5.0 / 0.0 / −1 / NaN; `ros2 topic hz`; `/clear` и `ros2 action list -t`; `check_practice.py PR04`

## PR05

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Grok 4.7 (Cursor Agent)
- Среда или интерфейс агента: Cursor IDE
- Затронутые компоненты: пакет `course_bringup` (launch с namespace, remap, `IfCondition` для MCAP), `pose_relay` / `pose_subscriber`, QoS best_effort против reliable, `evidence/pr05`, workflow `pr05.yml`
- Характер помощи: launch-файл и ноды реле/подписчика, launch-тест с чистым завершением, съём qos-before/qos-after и проверка replay записи
- Как результат был проверен независимо: `python3 -m pytest src/patrol/test`; `python3 -m pytest src/course_bringup/test`; `ros2 launch course_bringup patrol.launch.py` в `/robot_a`; `ros2 topic echo` reliable (timeout, RELIABILITY) и best_effort (Pose); `ros2 bag info` — один топик `/robot_a/sensor_pose`; replay с `config/qos-overrides.yaml`; `check_practice.py PR05`

## PR06

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Grok 4.7 (Cursor Agent)
- Среда или интерфейс агента: Cursor IDE
- Затронутые компоненты: пакет `course_description` (Xacro, launch, RViz, тесты), `evidence/pr06`, workflow `pr06.yml`. Код ПР05 не изменялся
- Характер помощи: URDF/Xacro по размерам SDF, дерево tf, проверка parent лидара, съём `/tf_static` transient local против volatile, отдельная ветка с неверным parent
- Как результат был проверен независимо: `xacro` и `check_urdf`; `colcon test --packages-select course_description`; `ros2 topic info /tf_static --verbose`; echo transient_local (exit=0) и volatile (exit=124); `tf2_echo base_link lidar_link`; запуск RViz; тест parent падает на ветке `pr06-lidar-parent-broken` и проходит на main; `check_practice.py PR06`
