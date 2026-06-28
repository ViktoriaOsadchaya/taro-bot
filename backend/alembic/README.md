# Alembic — миграции PostgreSQL

## Команды

```bash
cd backend
source .venv/bin/activate

alembic upgrade head                              # применить все миграции
alembic revision --autogenerate -m "описание"     # сгенерировать миграцию из models/
alembic downgrade -1                              # откатить одну миграцию
alembic current                                   # текущая ревизия
alembic history                                   # список миграций
```

## Конфигурация

- `alembic.ini` — точка входа CLI
- `alembic/env.py` — async-движок, `DATABASE_URL` из `.env`
- `alembic/versions/` — файлы миграций

## Autogenerate

После изменения моделей в `app/models/`:

1. `alembic revision --autogenerate -m "..."`
2. Проверить сгенерированный файл — особенно **enum-значения** (должны быть lowercase, как в `StrEnum`)
3. `alembic upgrade head`
