import logging

from aiogram import Bot, Dispatcher

from app.bot.commands import commands, scope
from app.bot.handlers import register_handlers
from app.database.main import initialize_db
from app.config import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(config.BOT_TOKEN)
    await bot.set_my_commands(commands, scope)

    dp = Dispatcher(bot)
    register_handlers(dp)

    bot_info = await bot.get_me()
    logger.info(bot_info)

    initialize_db()
    await dp.start_polling()
