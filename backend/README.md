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

## Интеграция Mini App (фронтенд)

**Base URL API:** `VITE_API_URL` = ngrok на порт **8000** (не URL фронта).

### Порядок запросов (карта дня)

```
1. POST {API}/api/v1/auth/telegram
   body: { "init_data": "<Telegram.WebApp.initData>" }
   → { "access_token": "...", "user": {...} }

2. POST {API}/api/v1/readings/sessions/
   header: Authorization: Bearer <access_token>
   body: { "spread_type": "card_of_day" }

3. POST {API}/api/v1/readings/sessions/draw
   header: Authorization: Bearer <access_token>
   → карта; при последней карте — interpretation в reading
```

### Типы раскладов (`spread_type`)

| UI | `spread_type` |
|----|----------------|
| Карта дня | `card_of_day` |
| Прошлое · настоящее · будущее | `past_present_future` |
| Свой вопрос | `free_question` (+ поле `question`) |

### Чего нет в API

Эндпоинты вроде `/spreads/daily` **не существуют** — будет 404.
Полный список: Swagger `http://127.0.0.1:8000/docs` или `app/api/README.md`.

CORS на бэкенде разрешает запросы с `*.ngrok-free.dev` и localhost.

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2026-06-28 | Alembic: первая миграция `initial schema` (users, tarot_cards, readings, reading_cards) |
