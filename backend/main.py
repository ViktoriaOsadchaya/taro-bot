"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.api_router import api_router
from app.api.routers import health, index
from app.core.container import container
from app.core.exception_handlers import register_exception_handlers
from app.core.redis_helper import redis_helper

PUBLIC_PATHS = {"/", "/health/", "/health", "/api/v1/auth/telegram"}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifecycle: закрытие Redis при остановке процесса."""
    yield
    await redis_helper.close()


def _configure_openapi(app: FastAPI) -> None:
    """Добавляет Bearer JWT в OpenAPI для Swagger."""

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})
        schema["components"]["securitySchemes"]["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }

        for path, path_item in schema.get("paths", {}).items():
            normalized = path.rstrip("/") if path != "/" else path
            if normalized in PUBLIC_PATHS or path in PUBLIC_PATHS:
                continue
            for operation in path_item.values():
                if isinstance(operation, dict):
                    operation["security"] = [{"BearerAuth": []}]

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi


def create_app() -> FastAPI:
    """Фабрика FastAPI-приложения с Dishka и обработчиками ошибок."""
    app = FastAPI(
        title="Taro Bot API",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    setup_dishka(container, app)
    app.include_router(index.router, tags=["system"])
    app.include_router(health.router, prefix="/health", tags=["system"])
    app.include_router(api_router, prefix="/api/v1", tags=["api"])
    _configure_openapi(app)
    return app


app = create_app()
