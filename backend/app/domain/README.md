# Domain — чистая доменная логика

> Журнал изменений: обновляется при каждом добавлении файлов в `app/domain/`.

## Назначение

Константы и функции без зависимостей от БД, HTTP и Redis.
Используются сервисами для валидации раскладов и формирования промптов LLM.

## Созданные файлы

| Файл | Описание |
|------|----------|
| `spread_config.py` | Конфиг типов раскладов, маппинг position_key, подписи для UI/LLM |
| `__init__.py` | Реэкспорт публичного API домена |

## spread_config.py — содержимое

### `SpreadDefinition` (dataclass)
- `cards_count` — сколько карт нужно вытянуть (1 или 3)
- `requires_question` — обязателен ли текст вопроса
- `title_ru`, `description_ru` — для меню бота и API

### `SPREAD_DEFINITIONS`
| SpreadType | cards | question |
|------------|-------|----------|
| `card_of_day` | 1 | нет |
| `past_present_future` | 3 | нет |
| `free_question` | 3 | да |

### `POSITION_KEYS_BY_SPREAD`
- Карта дня → `[day]`
- PPP → `[past, present, future]`
- Свободный вопрос → `[insight_1, insight_2, insight_3]`

### `POSITION_LABELS_RU`
Человекочитаемые названия позиций для промпта и Telegram-сообщений.

### Функции
- `get_spread_definition(spread_type)` — конфиг расклада
- `get_position_key(spread_type, position_index)` — ключ позиции по индексу

### `prompt_templates.py` (NEW)
- `build_system_prompt()` — роль таролога для LLM
- `build_user_prompt(spread_type, question, drawn_cards)` — карты и вопрос

## Правила

- Не импортировать `sqlalchemy`, `fastapi`, `redis` в этой папке
- Новые enum — в `app/models/enums.py`; здесь только конфигурация и чистые функции

## TODO

- [ ] `prompt_templates.py` — шаблоны system/user промптов для LLM
- [ ] `reading_session.py` — dataclass Redis-сессии (без клиента Redis)

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | Создан `spread_config.py`; добавлен `prompt_templates.py` |
