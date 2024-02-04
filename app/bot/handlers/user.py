from functools import wraps
from typing import Any, Dict, List, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.imager.main import accents, colors, styles
from app.spotify.user import SpotifyNowUser


# TODO make a validation.py and put color, accent, style validation funcs in there

def valid_user(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user = SpotifyNowUser(message.from_id)
        if not user.fetch():
            await message.answer('User not found in the database')
            return
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
    if not name or '@' in name: # TODO regex check
        await message.answer(f'Special characters and emojis are not allowed')
        return

    user = SpotifyNowUser(message.from_id)
    user.update({'name': name})
    await message.answer(
        f'Name successfully updated to *{name}*'
    )


@valid_user
async def update_user_style(message: Message):
    style = message.get_args()
    if not style or not valid(style, styles):
        await message.answer(f'Unsupported style: *{style}*')
        return

    user = SpotifyNowUser(message.from_id)
    user.update({'style': style})
    await message.answer(
        f'Style successfully updated to *{style}*'
    )


@valid_user
async def update_user_color(message: Message):
    color = message.get_args()
    if not color or not valid(color, colors):
        await message.answer(f'Unsupported color: *{color}*')
        return

    user = SpotifyNowUser(message.from_id)
    user.update({'color': color})
    await message.answer(
        f'Color successfully updated to *{color}*'
    )


@valid_user
async def update_user_accent(message: Message):
    accent = message.get_args()
    if not accent or not valid(accent, accents):
        await message.answer(f'Unsupported accent: *{accent}*')
        return

    user = SpotifyNowUser(message.from_id)
    user.update({'accent': accent})
    await message.answer(
        f'Accent successfully updated to *{accent}*'
    )


@valid_user
async def send_now_playing(message: Message):
    spotify_user = SpotifyNowUser(message.from_id)

    # TODO put all of this in a function in spotifynowuser, no dbuser access from here

    user = spotify_user.fetch()
    if not user or not user.token:
        return # not linked

    track = spotify_user.now_playing()
    if not track:
        await message.answer(
            f'You are not listening to anything on Spotify at the moment.'
        )
        return

    style = styles[user.style](colors[user.color], accents[user.accent])
    image = style.now(track, user)

    markup = button_markup('Play on Spotify', track.url)
    await message.reply_photo(
        image,
        reply_markup=markup
    )


async def send_top_chart(message: Message):
    ...

