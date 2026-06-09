"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.api.router import api_router, health_router
from app.core.container import container
from app.core.exception_handlers import register_exception_handlers
from app.core.redis_helper import redis_helper


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifecycle: закрытие Redis при остановке процесса."""
    yield
    await redis_helper.close()


def create_app() -> FastAPI:
    """Фабрика FastAPI-приложения с Dishka и обработчиками ошибок."""
    app = FastAPI(
        title="Taro Bot API",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    setup_dishka(container, app)
    app.include_router(health_router)
    app.include_router(api_router)
    return app


app = create_app()
