from dishka import Provider, Scope, provide

from app.api.schemas.reading_session_dto import DrawnCardSessionDTO
from app.domain.prompt_templates import build_system_prompt, build_user_prompt
from app.infrastructure.llm_client import LlmClient
from app.models.enums import SpreadType


class InterpretationService:
    """
    Генерация текстового толкования расклада через LLM.

    Формирует промпт из карт и вопроса, вызывает ProxyAPI.
    Используется ReadingSessionService при завершении расклада.
    """

    def __init__(self, llm_client: LlmClient) -> None:
        self.llm_client = llm_client

    async def generate(
        self,
        spread_type: SpreadType,
        question: str | None,
        drawn_cards: list[DrawnCardSessionDTO],
    ) -> str:
        """
        Запрашивает у LLM толкование выпавших карт.

        ***drawn_cards: все карты сессии с position_key и is_reversed***
        """
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(spread_type, question, drawn_cards)
        return await self.llm_client.complete_chat(system_prompt, user_prompt)


class InterpretationServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def interpretation_service(self, llm_client: LlmClient) -> InterpretationService:
        return InterpretationService(llm_client)
