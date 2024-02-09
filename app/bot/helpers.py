from functools import wraps
from typing import Any, Dict, List, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.config import config
from app.spotify.user import SpotifyNowUser


def valid_user(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user = SpotifyNowUser(message.from_id)
        if not user.fetch():
            return await message.answer('You need to /link your Spotify account with me first.')
        return await func(message, *args, **kwargs)
    return wrapper


def button_markup(text: str, url: str):
    button = InlineKeyboardButton(text, url) # type: ignore
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(button)
    return markup


def valid(item: str, item_list: Union[List[str], Dict[str, Any]]):
    item_list = [x.lower() for x in list(item_list)]
    return item.lower() in item_list


async def get_avatar(message: Message, avatar: str) -> str:
    if avatar == config.DEFAULT_AVATAR:
        pics = await message.bot.get_user_profile_photos(message.from_user.id, limit=1)
        if not pics['photos']:
            avatar = config.DEFAULT_AVATAR
        else:
            avatar = pics['photos'][0][0]['file_id']

    avatar_file = await message.bot.get_file(avatar)
    return await avatar_file.get_url()

