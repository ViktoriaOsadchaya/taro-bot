# Routers — HTTP endpoints

> Журнал изменений: обновляется при каждом добавлении файлов в `app/api/routers/`.
> Стандарты кода: см. [README_RULES.md](README_RULES.md).

## Назначение

Тонкий HTTP-слой: валидация входа, `FromDishka[Service]`, возврат DTO.
Без SQL и без бизнес-логики.

## Созданные файлы

| Файл | prefix | tags | Endpoints |
|------|--------|------|-----------|
| `health.py` | `/health` | system | GET `` — liveness (**публичный**) |
| `spreads.py` | `/spreads` | spreads | GET `/types` |
| `cards.py` | `/cards` | cards | GET `` |
| `users.py` | `/users` | users | POST `/upsert` |
| `reading_sessions.py` | `/readings/sessions` | reading-sessions | POST ``, GET `/current`, DELETE `/current`, POST `/draw` |
| `readings.py` | `/readings` | readings | GET ``, GET `/{reading_id}` |
| `__init__.py` | — | — | экспорт модулей |

Подключение: `app/api/router.py` → `api_router` (prefix `/api/v1`) + `health_router`.

Точка входа: `app/main.py` (`uvicorn app.main:app`).

## Карта безопасности

| Endpoint | Доступ |
|----------|--------|
| GET `/health` | **Публичный** — без заголовков |
| Все `/api/v1/*` | `X-Internal-Token` (= `SECRET_KEY` или `BOT_TOKEN` из `.env`) |
| Сессии и история | + `X-Telegram-Id` (int ≥ 1) |

## Заголовки запросов

| Заголовок | Где обязателен | Описание |
|-----------|----------------|----------|
| `X-Internal-Token` | все `/api/v1/*` | shared secret бота и API |
| `X-Telegram-Id` | sessions, readings | ID пользователя Telegram |

## Зависимости

| Модуль | Описание |
|--------|----------|
| `app/api/deps/bot_auth.py` | `verify_internal_token`, `get_telegram_id` |

## Обработка ошибок

`APIException` → JSON `{"detail": "...", "code": "..."}` через `app/core/exception_handlers.py`.

## TODO

- [ ] Route-тесты (pytest + httpx)
- [ ] OpenAPI examples

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | Создан README с планом роутеров |
| 2025-06-09 | Реализованы 6 роутеров, deps, main.py, exception_handlers |
