from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


commands = [
    BotCommand(
        command='start',
        description=''
    ),
    BotCommand(
        command='help',
        description=''
    )
]

scope = BotCommandScopeAllPrivateChats()
