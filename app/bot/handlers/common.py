from typing import Optional

from aiogram.types import Message


async def send_help(message: Message):
    await message.answer(
        'stop it.'
        'get some help.'
    )


async def send_start(message: Message):
    param = message.get_args()

    if not param:
        await message.answer(
            'send welcome message'
            'use /link to start'
            'use /help to list all commands'
        )

    if param == 'auth_success_new':
        await message.answer(
            'send auth success message'
            'use /name name to set name'
            'use /style style to set style'
            'use /help to list all commands'
        )

    if param == 'auth_success':
        await message.answer(
            'send auth success message'
        )

    if param == 'auth_failed':
        await message.answer(
            'send auth failed message'
        )
