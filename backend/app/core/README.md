# Core — инфраструктурный слой

> Журнал изменений: обновляется при каждом добавлении файлов в `app/core/`.

## Назначение

Базовый каркас приложения: конфигурация, подключение к БД, DI-контейнер, общие исключения.
Не содержит бизнес-логики Таро.

## Созданные файлы

| Файл | Описание |
|------|----------|
| `base.py` | `Base` — DeclarativeBase с `primary_key`, `created_at`, `updated_at` и автогенерацией `__tablename__` |
| `config.py` | Pydantic Settings: БД, Redis, BOT_TOKEN, LLM (ProxyAPI), webhook |
| `database.py` | Legacy/async generators `get_session`, `get_readonly_session` (через `db_helper`) |
| `db_helper.py` | **NEW** — `DatabaseHelper`, async engine, `session_factory`, `pool_pre_ping` |
| `redis_helper.py` | **NEW** — `RedisHelper`, lazy-клиент Redis |
| `exceptions.py` | `APIException`, `NotFoundException`, `ConflictException`, `ValidationException`, `ExternalServiceException`, `UnauthorizedException` |
| `exception_handlers.py` | регистрация handler `APIException` → JSON в FastAPI |
| `container.py` | Dishka: DbProvider, RedisProvider, репозитории, сервисы, infrastructure |

## Dishka — зарегистрированные провайдеры

| Provider | Scope | Что отдаёт |
|----------|-------|------------|
| `DbProvider` | REQUEST | `AsyncSession` (commit/rollback) |
| `RedisProvider` | APP | `Redis` |
| `UserRepoProvider` | REQUEST | `UserRepository` |
| `TarotCardRepoProvider` | REQUEST | `TarotCardRepository` |
| `ReadingRepoProvider` | REQUEST | `ReadingRepository` |
| `ReadingSessionStoreProvider` | REQUEST | `ReadingSessionStore` |
| `LlmClientProvider` | APP | `LlmClient` |
| `UserServiceProvider` | REQUEST | `UserService` |
| `SpreadServiceProvider` | REQUEST | `SpreadService` |
| `TarotCardServiceProvider` | REQUEST | `TarotCardService` |
| `ReadingServiceProvider` | REQUEST | `ReadingService` |
| `InterpretationServiceProvider` | REQUEST | `InterpretationService` |
| `ReadingSessionServiceProvider` | REQUEST | `ReadingSessionService` |

## Зависимости между файлами

```
config.py → db_helper.py → container.py
exceptions.py ← repositories, services, routers
exception_handlers.py ← main.py
base.py ← models/
```

## TODO

- [ ] Alembic-миграции

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | `exception_handlers.py`, `UnauthorizedException` |
