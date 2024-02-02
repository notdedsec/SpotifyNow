from aiogram.types import Message


async def send_TODO(message: Message):
    reply = 'TODO'
    await message.answer(reply)
