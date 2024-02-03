from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


commands = [
    BotCommand(
        command='start',
        description='hello world!'
    ),
    BotCommand(
        command='help',
        description='get some help!'
    )
]

scope = BotCommandScopeAllPrivateChats()
