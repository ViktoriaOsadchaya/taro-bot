# Schemas — Pydantic DTO

> Журнал изменений: обновляется при каждом добавлении файлов в `app/api/schemas/`.

## Назначение

Контракты данных между сервисами, роутерами и (в будущем) Telegram-handlers.
ORM-модели наружу не отдаются.

## Созданные файлы

| Файл | DTO |
|------|-----|
| `user_dto.py` | `UserUpsertDTO`, `UserReadDTO` |
| `spread_dto.py` | `SpreadTypeReadDTO` |
| `tarot_card_dto.py` | `TarotCardReadDTO` |
| `reading_session_dto.py` | `DrawnCardSessionDTO`, `ReadingSessionDTO`, `StartSessionDTO`, `DrawCardResultDTO` |
| `reading_dto.py` | `ReadingCardReadDTO`, `ReadingDetailDTO`, `ReadingHistoryItemDTO`, `ReadingHistoryDTO` |
| `__init__.py` | реэкспорт |

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | Созданы DTO для сервисного слоя |
