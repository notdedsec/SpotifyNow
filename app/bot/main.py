import asyncio

from aiogram import Bot, Dispatcher, executor

from app.bot.commands import commands, scope
from app.bot.handlers import register_handlers
from app.config import config

bot = Bot(config.BOT_TOKEN)
asyncio.run(bot.set_my_commands(commands, scope))
bot_info = asyncio.run(bot.get_me())

dp = Dispatcher(bot)
register_handlers(dp)


def initialize_bot():
    executor.start_polling(dp, skip_updates=True)

