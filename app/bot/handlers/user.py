import re

from aiogram.types import Message

from app.bot.helpers import get_avatar, valid_user, valid, button_markup
from app.imager.main import accents, colors, styles
from app.spotify.user import SpotifyNowUser
from app.config import config


async def link_user(message: Message):
    user = SpotifyNowUser(message.from_id, message.from_user.username)
    if not user.fetch():
        user.link()

    url = user.get_auth_url()
    markup = button_markup('Authorize', url)
    await message.answer(
        'Tap the button below to link your Spotify account. This will allow me to show what you are listening to on Spotify.',
        reply_markup=markup
    )


@valid_user
async def unlink_user(message: Message):
    user = SpotifyNowUser(message.from_id)
    user.unlink()
    await message.answer(
        'Your account has been unlinked.'
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

    user = spotify_user.fetch()
    if not user or not user.token:
        return await message.answer(f'You have not authorized me to access your Spotify information. Try the /link command.')

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

