"""
Асинхронный клиент Redis для FSM-сессий раскладов.

Единая точка создания подключения; закрывается при остановке приложения.
"""

from redis.asyncio import Redis

from app.core.config import settings


class RedisHelper:
    """Обёртка над redis.asyncio.Redis с настройками из config."""

    def __init__(self) -> None:
        self._client: Redis | None = None

    @property
    def client(self) -> Redis:
        """Лениво создаёт клиент Redis (decode_responses=True для JSON-строк)."""
        if self._client is None:
            self._client = Redis.from_url(
                settings.redis.url,
                decode_responses=settings.redis.decode_responses,
                socket_connect_timeout=settings.redis.socket_connect_timeout,
                socket_timeout=settings.redis.socket_timeout,
                retry_on_timeout=settings.redis.retry_on_timeout,
                health_check_interval=settings.redis.health_check_interval,
            )
        return self._client

    async def close(self) -> None:
        """Закрывает соединение при shutdown."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


redis_helper = RedisHelper()
