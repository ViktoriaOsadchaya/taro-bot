from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user_dto import UserReadDTO, UserUpsertDTO
from app.core.exceptions import NotFoundException
from app.repositories.user_repository import UserRepository


class UserService:
    """
    Бизнес-логика пользователей Telegram.

    Нужен для регистрации при /start и привязки раскладов к user_id.
    Используется роутерами auth/users и ReadingSessionService.
    """

    def __init__(self, session: AsyncSession, user_repo: UserRepository) -> None:
        self.session = session
        self.user_repo = user_repo

    async def upsert(self, data: UserUpsertDTO) -> UserReadDTO:
        """Создаёт или обновляет пользователя по данным из Telegram."""
        user = await self.user_repo.upsert_from_telegram(
            self.session,
            telegram_id=data.telegram_id,
            username=data.username,
            first_name=data.first_name,
            language_code=data.language_code,
        )
        if user is None:
            raise NotFoundException("Не удалось сохранить пользователя")
        return UserReadDTO.model_validate(user)

    async def get_by_telegram_id(self, telegram_id: int) -> UserReadDTO:
        """Возвращает пользователя по Telegram ID или 404."""
        user = await self.user_repo.find_by_field(self.session, "telegram_id", telegram_id)
        if user is None:
            raise NotFoundException("Пользователь не найден")
        return UserReadDTO.model_validate(user)


class UserServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_service(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
    ) -> UserService:
        return UserService(session, user_repo)
