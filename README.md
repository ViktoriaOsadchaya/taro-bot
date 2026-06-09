# Локальная инфраструктура Taro Bot

> Журнал изменений: обновляется при каждом добавлении файлов в репозиторий.

## Назначение

Корень монорепозитория: Docker-окружение для разработки и шаблон переменных окружения.

## Созданные файлы

| Файл | Описание |
|------|----------|
| `docker-compose.yml` | PostgreSQL 16 + Redis 7 с healthcheck и persistent volumes |
| `.env.example` | Шаблон `DATABASE_URL`, `REDIS_URL`, `BOT_TOKEN`, ключи LLM |
| `README.md` | Этот файл — карта проекта на уровне корня |

## docker-compose.yml

### Сервисы

- **postgres** — БД `taro_bot`, пользователь/пароль `postgres/postgres`, порт `5432`
- **redis** — кэш и FSM-сессии раскладов, порт `6379`, AOF-персистентность

### Запуск

```bash
docker compose up -d
cp .env.example .env
```

## Связь с backend

`DATABASE_URL` и `REDIS_URL` в `.env` должны совпадать с портами из compose.
Дефолты в `backend/app/core/config.py` настроены под этот compose.

## Следующие шаги

- [ ] `pyproject.toml` + Poetry
- [ ] Alembic-миграции
- [ ] Dockerfile для backend (опционально)

## История обновлений

| Дата | Изменение |
|------|-----------|
| 2025-06-09 | Создан `docker-compose.yml`, `.env.example`, корневой README |
