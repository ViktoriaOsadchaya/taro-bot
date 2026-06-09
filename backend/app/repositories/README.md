# Repositories — слой доступа к БД

> Журнал изменений: обновляется при каждом добавлении файлов в `app/repositories/`.
> Стандарты кода: см. [README_RULES.md](README_RULES.md).

## Назначение

Инкапсуляция SQLAlchemy-запросов. Сервисы вызывают только методы репозиториев.

## Базовый класс

| Файл | Описание |
|------|----------|
| `base_repository.py` | `BaseRepository[T]` — CRUD, пагинация, `find_by_field` и др. |

## Созданные репозитории

| Файл | Модель | Методы |
|------|--------|--------|
| `user_repository.py` | `User` | `get_by_telegram_id`, `upsert_from_telegram` |
| `tarot_card_repository.py` | `TarotCard` | `get_all_ordered`, `get_available_excluding`, `get_by_code` |
| `reading_repository.py` | `Reading` | `get_by_id_with_cards`, `get_by_id_for_user`, `get_completed_by_user_paginated`, `create_with_cards` |
| `__init__.py` | — | Экспорт классов и singleton-инстансов |

## Dishka Provider'ы

Каждый репозиторий экспортирует `*RepoProvider` (scope REQUEST).
Регистрация — в `app/core/container.py` → `ALL_PROVIDERS`.

Singleton-инстансы (`user_repository`, …) — для обратной совместимости и тестов.

## Использование в сервисах (план)

| Сервис | Репозитории |
|--------|-------------|
| `UserService` | `UserRepository` |
| `TarotCardService` | `TarotCardRepository` |
| `ReadingService` | `ReadingRepository`, `UserRepository` |

## TODO

- [ ] `ReadingSessionStore` — не репозиторий БД, а Redis-адаптер (отдельная папка или `infrastructure/`)
- [ ] Unit-тесты репозиториев с testcontainers

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | Созданы User, TarotCard, Reading репозитории + Provider'ы |
