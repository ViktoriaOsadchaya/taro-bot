# Models — SQLAlchemy ORM

> Журнал изменений: обновляется при каждом добавлении файлов в `app/models/`.

## Назначение

Персистентные сущности PostgreSQL для Таро-бота.
Все модели наследуют `app.core.base.Base` (поля `primary_key`, `created_at`, `updated_at`).

## ER-схема

```
User 1 ──< Reading 1 ──< ReadingCard >── 1 TarotCard
```

## Созданные файлы

| Файл | Таблица | Описание |
|------|---------|----------|
| `enums.py` | — | `SpreadType`, `ReadingStatus`, `Arcana`, `Suit`, `CardPositionKey` |
| `user.py` | `users` | Telegram-пользователь (`telegram_id` unique) |
| `tarot_card.py` | `tarot_cards` | Справочник 78 карт (seed-миграция) |
| `reading.py` | `readings` | Завершённый расклад + толкование LLM |
| `reading_card.py` | `reading_cards` | Карта в раскладе: позиция, reversed |
| `__init__.py` | — | Экспорт всех моделей для Alembic |

## Ключевые поля и ограничения

### users
- `telegram_id` — BigInteger, unique, index
- `language_code` — default `ru`

### readings
- Индекс `(user_id, created_at)` — для `/history`
- `question` — только для `FREE_QUESTION`
- `status` — `completed` | `failed`

### reading_cards
- Unique `(reading_id, position_index)`
- FK на `tarot_cards` с `ON DELETE RESTRICT`

## Что НЕ хранится в БД

- Активная сессия расклада (Redis, `ReadingSessionService` — TODO)
- Черновики до вызова LLM

## Связанные модули

- `app/domain/spread_config.py` — правила количества карт и position_key
- `app/repositories/` — доступ к таблицам

## TODO

- [ ] Alembic: первая миграция + seed 78 карт
- [ ] `alembic/env.py` — импорт `app.models`

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | Созданы все модели и enums; добавлены docstring и комментарии к полям |
