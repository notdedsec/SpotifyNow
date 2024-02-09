from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


commands = [
    BotCommand(
        command='start',
        description='Get started with SpotifyNow'
    ),
    BotCommand(
        command='help',
        description='Explain all commands'
    ),
    BotCommand(
        command='now',
        description='Share what you are listening to'
    ),
    BotCommand(
        command='link',
        description='Link your Spotify account'
    ),
    BotCommand(
        command='unlink',
        description='Unlink your Spotify account'
    ),
    BotCommand(
        command='name',
        description='Set your display name'
    ),
    BotCommand(
        command='style',
        description='Set your preferred style'
    ),
    BotCommand(
        command='color',
        description='Set your preferred color'
    ),
    BotCommand(
        command='accent',
        description='Set your preferred accent color'
    ),
    BotCommand(
        command='avatar',
        description='Set your profile picture'
    ),
]

scope = BotCommandScopeAllPrivateChats()
