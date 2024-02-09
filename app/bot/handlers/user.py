import re
from functools import wraps
from typing import Any, Dict, List, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.imager.main import accents, colors, styles
from app.spotify.user import SpotifyNowUser
from app.config import config
from app.bot.helpers import get_avatar


# TODO make a validation.py and put color, accent, style validation funcs in there

def valid_user(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user = SpotifyNowUser(message.from_id)
        if not user.fetch():
            return await message.answer('User not found in the database')
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


async def link_user(message: Message):
    user = SpotifyNowUser(message.from_id, message.from_user.username)
    if not user.fetch():
        user.link()

    url = user.get_auth_url()
    markup = button_markup('Authorize', url)
    await message.answer(
        'link_message',
        reply_markup=markup
    )


@valid_user
async def unlink_user(message: Message):
    user = SpotifyNowUser(message.from_id)
    user.unlink()
    await message.answer(
        'User has been unlinked'
    )


@valid_user
async def update_user_name(message: Message):
    name = message.get_args()
    if not name:
        return await message.answer(f'Name cannot be empty')
    if re.search(r'[^a-zA-Z0-9\s]', name):
        return await message.answer(f'Name cannot contain special characters')

    user = SpotifyNowUser(message.from_id)
    user.update({'name': name})
    await message.answer(
        f'Name successfully updated to *{name}*'
    )


@valid_user
async def update_user_style(message: Message):
    style = message.get_args()
    if not style or not valid(style, styles):
        return await message.answer(f'Unsupported style: *{style}*')

    user = SpotifyNowUser(message.from_id)
    user.update({'style': style})
    await message.answer(
        f'Style successfully updated to *{style}*'
    )


@valid_user
async def update_user_color(message: Message):
    color = message.get_args()
    if not color or not valid(color, colors):
        return await message.answer(f'Unsupported color: *{color}*')

    user = SpotifyNowUser(message.from_id)
    user.update({'color': color})
    await message.answer(
        f'Color successfully updated to *{color}*'
    )


@valid_user
async def update_user_accent(message: Message):
    accent = message.get_args()
    if not accent or not valid(accent, accents):
        return await message.answer(f'Unsupported accent: *{accent}*')

    user = SpotifyNowUser(message.from_id)
    user.update({'accent': accent})
    await message.answer(
        f'Accent successfully updated to *{accent}*'
    )


@valid_user
async def update_user_avatar(message: Message):
    args = message.get_args()
    if args and 'auto' in args.lower():
        avatar = config.DEFAULT_AVATAR
    elif not message.reply_to_message or not message.reply_to_message.photo:
        return await message.answer(f'Please reply to an image with the /avatar command.')
    else:
        avatar = message.reply_to_message.photo[-1].file_id

    user = SpotifyNowUser(message.from_id)
    user.update({'avatar': avatar})
    await message.answer(
        f'Avatar successfully updated.'
    )


@valid_user
async def send_now_playing(message: Message):
    spotify_user = SpotifyNowUser(message.from_id)

    # TODO put all of this in a function in spotifynowuser, no dbuser access from here

    user = spotify_user.fetch()
    if not user or not user.token:
        return await message.answer(f'You have not linked your Spotify account yet.')

    track = spotify_user.now_playing()
    if not track:
        return await message.answer(f'You are not listening to anything on Spotify at the moment.')

    user.avatar = await get_avatar(message, user.avatar)

    style = styles[user.style](colors[user.color], accents[user.accent])
    image = style.now(track, user)

    markup = button_markup('Play on Spotify', track.url)
    await message.reply_photo(
        image,
        reply_markup=markup
    )


async def send_top_chart(message: Message):
    ...

