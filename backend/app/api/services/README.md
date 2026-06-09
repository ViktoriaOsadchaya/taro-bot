# Services — бизнес-логика

> Журнал изменений: обновляется при каждом добавлении файлов в `app/api/services/`.
> Стандарты кода: см. [README_RULES.md](README_RULES.md).

## Назначение

Ядро приложения: оркестрация репозиториев, Redis, LLM.
Роутеры и handlers бота вызывают **только** сервисы.

## Созданные сервисы

| Файл | Класс | Зависимости | Методы |
|------|-------|-------------|--------|
| `user_service.py` | `UserService` | `AsyncSession`, `UserRepository` | `upsert`, `get_by_telegram_id` |
| `spread_service.py` | `SpreadService` | — (domain config) | `list_spread_types` |
| `tarot_card_service.py` | `TarotCardService` | `AsyncSession`, `TarotCardRepository` | `list_all`, `draw_random` |
| `reading_service.py` | `ReadingService` | `AsyncSession`, `ReadingRepository` | `get_history`, `get_detail`, `save_completed`, `save_failed` |
| `interpretation_service.py` | `InterpretationService` | `LlmClient` | `generate` |
| `reading_session_service.py` | `ReadingSessionService` | Store, User, TarotCard, Reading, Interpretation | `start_session`, `get_current_session`, `cancel_session`, `draw_card` |
| `__init__.py` | — | экспорт классов | — |

## Dishka Provider'ы

Каждый сервис имеет `*ServiceProvider` (scope REQUEST) в конце файла.
Регистрация — `app/core/container.py` → `ALL_PROVIDERS`.

| Provider | Scope |
|----------|-------|
| `UserServiceProvider` | REQUEST |
| `SpreadServiceProvider` | REQUEST |
| `TarotCardServiceProvider` | REQUEST |
| `ReadingServiceProvider` | REQUEST |
| `InterpretationServiceProvider` | REQUEST |
| `ReadingSessionServiceProvider` | REQUEST |

## DTO (вход/выход)

Схемы в `app/api/schemas/`:

- `user_dto.py` — `UserUpsertDTO`, `UserReadDTO`
- `spread_dto.py` — `SpreadTypeReadDTO`
- `tarot_card_dto.py` — `TarotCardReadDTO`
- `reading_session_dto.py` — `ReadingSessionDTO`, `StartSessionDTO`, `DrawCardResultDTO`
- `reading_dto.py` — `ReadingDetailDTO`, `ReadingHistoryDTO`

## Поток гадания (ReadingSessionService)

```
start_session → Redis
draw_card (×N) → TarotCardService.draw_random → Redis
последняя карта → InterpretationService → ReadingService.save_completed → delete Redis
ошибка LLM → ReadingService.save_failed → raise ExternalServiceException
```

## Исключения

| Ситуация | Исключение |
|----------|------------|
| Нет сессии / пользователя / расклада | `NotFoundException` |
| Все карты уже вытянуты | `ConflictException` |
| Невалидный вопрос | `ValidationException` |
| Redis / LLM недоступны | `ExternalServiceException` |

## TODO

- [ ] Unit-тесты сервисов с mock репозиториев
- [ ] Лимит раскладов в день на пользователя

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | Созданы все 6 сервисов, DTO, Provider'ы, регистрация в container |
