from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Доступ к таблице users.

    Используется UserService и ReadingService для upsert пользователя Telegram
    и проверки владельца расклада.
    """

    def __init__(self) -> None:
        super().__init__(User)

    async def upsert_from_telegram(
        self,
        session: AsyncSession,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        language_code: str = "ru",
    ) -> User:
        """
        Создаёт пользователя или обновляет профиль при повторном /start.

        ***telegram_id: уникальный идентификатор из Telegram***
        """
        user = await self.find_by_field(session, "telegram_id", telegram_id)
        if user is None:
            return await self.create(
                session,
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                language_code=language_code,
            )

        return await self.update(
            session,
            user.primary_key,
            username=username,
            first_name=first_name,
            language_code=language_code,
        )


user_repository = UserRepository()
