from dishka import Provider, Scope, provide

from app.api.schemas.spread_dto import SpreadTypeReadDTO
from app.domain.spread_config import SPREAD_DEFINITIONS


class SpreadService:
    """
    Справочник типов раскладов для меню бота и API.

    Не обращается к БД — данные из domain/spread_config.
    Используется роутером GET /spreads/types и handlers бота.
    """

    async def list_spread_types(self) -> list[SpreadTypeReadDTO]:
        """Возвращает все доступные типы раскладов с описаниями."""
        return [
            SpreadTypeReadDTO.model_validate(definition, from_attributes=True)
            for definition in SPREAD_DEFINITIONS.values()
        ]


class SpreadServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def spread_service(self) -> SpreadService:
        return SpreadService()
