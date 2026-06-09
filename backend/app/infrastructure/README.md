# Infrastructure — внешние адаптеры

> Журнал изменений: обновляется при каждом добавлении файлов в `app/infrastructure/`.

## Назначение

Клиенты Redis и LLM. Не SQLAlchemy, не HTTP-роутеры.

## Созданные файлы

| Файл | Класс | Provider | Описание |
|------|-------|----------|----------|
| `reading_session_store.py` | `ReadingSessionStore` | `ReadingSessionStoreProvider` (REQUEST) | CRUD Redis-ключей `reading_session:{telegram_id}` |
| `llm_client.py` | `LlmClient` | `LlmClientProvider` (APP) | HTTP chat/completions через ProxyAPI |
| `__init__.py` | — | — | экспорт |

## Связанные файлы core

| Файл | Описание |
|------|----------|
| `app/core/redis_helper.py` | Singleton Redis-клиент из `settings.redis` |

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | ReadingSessionStore, LlmClient, redis_helper |
