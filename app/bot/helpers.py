from aiogram.types import Message
from app.config import config


async def get_avatar(message: Message, avatar: str) -> str:
    if avatar == config.DEFAULT_AVATAR:
        pics = await message.bot.get_user_profile_photos(message.from_user.id, limit=1)
        if not pics['photos']:
            avatar = config.DEFAULT_AVATAR
        else:
            avatar = pics['photos'][0][0]['file_id']

    avatar_file = await message.bot.get_file(avatar)
    return await avatar_file.get_url()

