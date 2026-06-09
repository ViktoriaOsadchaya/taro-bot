# API — HTTP и сервисный слой

> Журнал изменений: обновляется при каждом добавлении файлов в `app/api/`.

## Назначение

REST API для Telegram-бота и WebApp.
Бизнес-логика — в `services/`, маршруты — в `routers/`.

## Структура

```
api/
├── deps/          # FastAPI dependencies (auth)
├── routers/       # FastAPI APIRouter
├── schemas/       # Pydantic DTO
├── services/      # Бизнес-логика
└── router.py      # Сборка роутеров
```

## Endpoints (base: `/api/v1`)

| Method | Path | Handler |
|--------|------|---------|
| GET | `/health` | liveness (вне v1) |
| GET | `/spreads/types` | типы раскладов |
| GET | `/cards` | справочник карт |
| POST | `/users/upsert` | регистрация пользователя |
| POST | `/readings/sessions` | старт расклада |
| GET | `/readings/sessions/current` | текущая сессия |
| DELETE | `/readings/sessions/current` | отмена |
| POST | `/readings/sessions/draw` | вытянуть карту |
| GET | `/readings` | история |
| GET | `/readings/{id}` | детали расклада |

## Запуск

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Статус

| Компонент | Статус |
|-----------|--------|
| `routers/` | **Готово** |
| `services/` | **Готово** |
| `schemas/` | **Готово** |
| `deps/` | **Готово** |
| `main.py` | **Готово** |

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | Роутеры, deps, main.py, exception_handlers |
