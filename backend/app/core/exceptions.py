"""
Иерархия прикладных исключений.

Сервисы бросают наследников APIException; глобальный handler (exception_handlers.py)
превращает их в JSON-ответы с нужным HTTP-кодом.
"""


class APIException(Exception):
    """Базовое исключение API с HTTP-статусом и машинным кодом ошибки."""

    def __init__(
        self,
        message: str = "Произошла ошибка",
        status_code: int = 400,
        code: str = "bad_request",
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class NotFoundException(APIException):
    """Сущность не найдена (404)."""

    def __init__(self, message: str = "Ресурс не найден") -> None:
        super().__init__(message=message, status_code=404, code="not_found")


class ConflictException(APIException):
    """Конфликт состояния, напр. активная сессия уже существует (409)."""

    def __init__(self, message: str = "Конфликт данных") -> None:
        super().__init__(message=message, status_code=409, code="conflict")


class ValidationException(APIException):
    """Ошибка валидации бизнес-правил (422)."""

    def __init__(self, message: str = "Некорректные данные") -> None:
        super().__init__(message=message, status_code=422, code="validation_error")


class ExternalServiceException(APIException):
    """Ошибка внешнего сервиса, напр. LLM или Redis (502)."""

    def __init__(self, message: str = "Внешний сервис недоступен") -> None:
        super().__init__(message=message, status_code=502, code="external_service_error")


class UnauthorizedException(APIException):
    """Ошибка аутентификации (401)."""

    def __init__(self, message: str = "Недостаточно прав") -> None:
        super().__init__(message=message, status_code=401, code="unauthorized")
