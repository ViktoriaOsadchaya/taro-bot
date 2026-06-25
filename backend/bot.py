"""
Telegram-бот для запуска Mini App (WebApp).

Отдельный процесс от FastAPI. Запуск:
    cd backend && source .venv/bin/activate && python bot.py

Переменные окружения (.env):
    BOT_TOKEN   — токен от @BotFather
    WEBAPP_URL  — публичный HTTPS-адрес фронтенда (ngrok)
"""

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

START_MESSAGE = (
    "🔮 Добро пожаловать в Taro Bot!\n\n"
    "Нажми кнопку ниже, чтобы открыть приложение с раскладами Таро."
)
OPEN_APP_BUTTON_TEXT = "Открыть приложение"


def _validate_env() -> None:
    """Проверяет обязательные переменные окружения перед стартом."""
    missing: list[str] = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not WEBAPP_URL:
        missing.append("WEBAPP_URL")
    if missing:
        logger.error("Не заданы переменные окружения: %s", ", ".join(missing))
        logger.error("Скопируй backend/.env.example в backend/.env и заполни значения.")
        sys.exit(1)
    if not WEBAPP_URL.startswith("https://"):
        logger.error("WEBAPP_URL должен начинаться с https:// (Telegram требует HTTPS)")
        sys.exit(1)


def _build_webapp_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой открытия Mini App."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=OPEN_APP_BUTTON_TEXT,
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )


async def handle_start(message: Message) -> None:
    """Обработчик /start: приветствие и кнопка WebApp."""
    await message.answer(
        START_MESSAGE,
        reply_markup=_build_webapp_keyboard(),
    )


async def main() -> None:
    """Точка входа: long polling."""
    _validate_env()

    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.message.register(handle_start, CommandStart())

    logger.info("Бот запущен. WebApp URL: %s", WEBAPP_URL)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
