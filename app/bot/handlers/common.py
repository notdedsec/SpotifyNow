from typing import Optional

from aiogram.types import Message


async def send_help(message: Message):
    await message.answer(
        "Tap /now to share what you're listening to on Spotify. "
        "You can also use it in inline mode by typing @SpotifyNowBot in any chat.\n"
        "If you're new, you need to /link your account to get started. "
        "You can always /unlink it whenever you feel like.\n"
        "If you're facing issues, try to /unlink and /link again. "
        "No good? Try restarting Spotify. "
        "If the issue persists, report it to @notdedsec.\n"
    )


async def send_start(message: Message):
    param = message.get_args()

    if not param:
        await message.answer(
            "Hi! I'm SpotifyNow and I you flex what you're listening to on Spotify. "
            "Tap /now to get started or /help to learn more."
        )

    if param == 'auth_success_new':
        await message.answer(
            "Yay! Your Spotify account has been linked. "
            "Tap /now anytime to flex what you're listening to. "
            "You can also use it in inline mode by typing @SpotifyNowBot in any chat."
        )
        # TODO add /name /style /accent /color /avatar (maybe /customize)

    if param == 'auth_success':
        await message.answer(
            "Yay! Your Spotify account has been linked."
        )

    if param == 'auth_failed':
        await message.answer(
            "Something went wrong. Try to /relink your account."
        )
