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
