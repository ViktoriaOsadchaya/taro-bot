"""
Telegram-бот для запуска Mini App (WebApp).

Отдельный процесс от FastAPI. Запуск:
    cd backend && source .venv/bin/activate && python bot.py

Переменные окружения (.env):
    BOT_TOKEN     — токен от @BotFather
    WEBAPP_URL    — публичный HTTPS-адрес фронтенда (ngrok)
    API_BASE_URL  — адрес FastAPI (по умолчанию http://127.0.0.1:8000)
"""

import asyncio
import logging
import os
import sys

import httpx
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").strip().rstrip("/")

START_MESSAGE = (
    "🔮 Добро пожаловать в Taro Bot!\n\n"
    "Нажми кнопку ниже, чтобы открыть приложение с раскладами Таро."
)
HELP_MESSAGE = (
    "📖 <b>Как устроен Taro Bot</b>\n\n"
    "Бот для тех, кто хочет заглянуть в карты и посмотреть на ситуацию "
    "со стороны — без воды и без мистического тумана.\n\n"
    "<b>Расклады:</b>\n"
    "▸ <b>Карта дня</b> — один акцент на сегодня: настроение, совет, на что обратить внимание.\n"
    "▸ <b>Прошлое · настоящее · будущее</b> — взгляд на ситуацию во времени: "
    "откуда пришли, где стоите, куда движетесь.\n"
    "▸ <b>Свой вопрос</b> — задай то, что волнует (отношения, работа, решение), "
    "и три карты соберут ответ.\n\n"
    "<b>Как пользоваться:</b>\n"
    "1. Нажми «Открыть приложение» или кнопку меню внизу чата.\n"
    "2. Выбери расклад и следуй подсказкам.\n"
    "3. История сохраняется — можно вернуться к прошлым толкованиям.\n\n"
    "<b>Команды:</b>\n"
    "/start — начать\n"
    "/help — эта справка"
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


async def _register_user(message: Message) -> None:
    """Создаёт или обновляет пользователя в БД через внутренний API."""
    if message.from_user is None:
        return

    telegram_user = message.from_user
    payload = {
        "telegram_id": telegram_user.id,
        "username": telegram_user.username,
        "first_name": telegram_user.first_name,
        "language_code": telegram_user.language_code or "ru",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/bot/users/upsert",
                json=payload,
                headers={"X-Internal-Token": BOT_TOKEN},
            )
            response.raise_for_status()
        logger.info("Пользователь %s зарегистрирован", telegram_user.id)
    except httpx.HTTPError as exc:
        logger.warning("Не удалось зарегистрировать пользователя %s: %s", telegram_user.id, exc)


async def handle_start(message: Message) -> None:
    """Обработчик /start: регистрация, приветствие и кнопка WebApp."""
    await _register_user(message)
    await message.answer(
        START_MESSAGE,
        reply_markup=_build_webapp_keyboard(),
    )


async def handle_help(message: Message) -> None:
    """Обработчик /help: справка по раскладам и командам."""
    await message.answer(
        HELP_MESSAGE,
        reply_markup=_build_webapp_keyboard(),
        parse_mode="HTML",
    )


async def main() -> None:
    """Точка входа: long polling."""
    _validate_env()

    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.message.register(handle_start, CommandStart())
    dispatcher.message.register(handle_help, Command("help"))

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Начать и открыть приложение"),
            BotCommand(command="help", description="Справка по раскладам"),
        ]
    )

    logger.info("Бот запущен. WebApp URL: %s, API: %s", WEBAPP_URL, API_BASE_URL)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
