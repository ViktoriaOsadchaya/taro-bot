"""
HTTP-клиент для LLM через ProxyAPI (OpenAI-compatible chat completions).
"""

import asyncio

import httpx
from dishka import Provider, Scope, provide

from app.core.config import logger, settings
from app.core.exceptions import ExternalServiceException


class LlmClient:
    """
    Асинхронные запросы к LLM API.

    Используется InterpretationService для генерации толкования расклада.
    Поддерживает retry из settings.llm.
    """

    def __init__(self) -> None:
        self._settings = settings.llm

    async def complete_chat(self, system_prompt: str, user_prompt: str) -> str:
        """
        Отправляет chat completion и возвращает текст ответа модели.

        ***system_prompt: роль таинственного таролога***
        ***user_prompt: карты, позиции и вопрос пользователя***
        """
        if not self._settings.is_configured:
            raise ExternalServiceException("LLM API не настроен (url/key/model)")

        url = self._settings.api_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._settings.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.8,
        }

        last_error: Exception | None = None
        attempts = self._settings.retry_count + 1

        for attempt in range(attempts):
            try:
                async with httpx.AsyncClient(timeout=self._settings.timeout) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    if not content or not str(content).strip():
                        raise ExternalServiceException("LLM вернул пустой ответ")
                    return str(content).strip()
            except ExternalServiceException:
                raise
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "LLM request failed (attempt %s/%s): %s",
                    attempt + 1,
                    attempts,
                    exc,
                )
                if attempt < attempts - 1:
                    await asyncio.sleep(self._settings.retry_delay)

        raise ExternalServiceException("Не удалось получить толкование от LLM") from last_error


class LlmClientProvider(Provider):
    scope = Scope.APP

    @provide
    def llm_client(self) -> LlmClient:
        return LlmClient()
