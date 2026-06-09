from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

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
            SpreadTypeReadDTO(
                spread_type=definition.spread_type,
                cards_count=definition.cards_count,
                requires_question=definition.requires_question,
                title_ru=definition.title_ru,
                description_ru=definition.description_ru,
            )
            for definition in SPREAD_DEFINITIONS.values()
        ]


class SpreadServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def spread_service(self) -> SpreadService:
        return SpreadService()
