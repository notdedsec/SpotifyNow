import asyncio

from aiogram import Bot, Dispatcher, executor

from app.bot.commands import commands, scope
from app.bot.handlers import register_handlers
from app.config import config


def main():
    bot = Bot(config.BOT_TOKEN)
    asyncio.run(bot.set_my_commands(commands, scope))

    dp = Dispatcher(bot)
    register_handlers(dp)

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()

