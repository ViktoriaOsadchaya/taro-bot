"""Глобальные обработчики исключений FastAPI."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import APIException


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует преобразование APIException в JSON-ответы."""

    @app.exception_handler(APIException)
    async def api_exception_handler(_request: Request, exc: APIException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )
