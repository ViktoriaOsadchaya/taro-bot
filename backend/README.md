# Backend — Taro Bot

> Журнал изменений: обновляется при каждом добавлении файлов в `backend/`.

## Назначение

Асинхронный Python-бэкенд: FastAPI + SQLAlchemy + Dishka + aiogram (бот — позже).

## Структура `app/`

```
app/
├── core/           # Конфиг, БД, DI, исключения
├── domain/         # Чистые константы и правила раскладов
├── models/         # SQLAlchemy ORM
├── repositories/   # Доступ к БД
├── api/
│   ├── routers/    # HTTP endpoints (TODO)
│   └── services/   # Бизнес-логика (TODO)
```

## Слои (строго сверху вниз)

```
Router → Service → Repository → Database
```

## Созданные модули

| Папка | Статус | README |
|-------|--------|--------|
| `core/` | Готово (базовый скелет) | [core/README.md](app/core/README.md) |
| `domain/` | Готово | [domain/README.md](app/domain/README.md) |
| `models/` | Готово | [models/README.md](app/models/README.md) |
| `repositories/` | Готово (3 репозитория) | [repositories/README.md](app/repositories/README.md) |
| `api/services/` | **Готово** — 6 сервисов | [api/services/README.md](app/api/services/README.md) |
| `api/routers/` | **Готово** — 6 роутеров | [api/routers/README.md](app/api/routers/README.md) |

## Правила кода

В каждой папке слоя есть `README_RULES.md` с обязательными стандартами (Dishka, docstring, без SQL в сервисах).

## Миграции БД (Alembic)

```bash
# из backend/, после docker compose up -d
source .venv/bin/activate
alembic upgrade head          # применить миграции
alembic revision --autogenerate -m "описание"  # новая миграция после изменения models/
alembic downgrade -1          # откат последней миграции
```

URL берётся из `.env` (`DATABASE_URL`) через `alembic/env.py`.

Удобная обёртка: `python scripts/init_db.py` (= `alembic upgrade head`).

Если таблицы уже созданы вручную (старый `create_all`), один раз:
`alembic stamp head` — пометить БД как актуальную без повторного создания таблиц.

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2026-06-28 | Alembic: первая миграция `initial schema` (users, tarot_cards, readings, reading_cards) |
