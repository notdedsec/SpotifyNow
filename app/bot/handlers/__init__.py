from aiogram import Dispatcher
from aiogram.types import ChatType

from app.bot.handlers import user, admin, common


def register_handlers(dp: Dispatcher):

    dp.register_message_handler(
        common.send_help,
        commands=['help'],
        chat_type=ChatType.PRIVATE
    )

    dp.register_message_handler(
        common.send_start,
        commands=['start'],
        chat_type=ChatType.PRIVATE
    )

    dp.register_message_handler(
        admin.send_TODO,
        commands=['todo'],
        chat_type=ChatType.PRIVATE
    )

    dp.register_message_handler(
        user.link_user,
        commands=['link', 'relink'],
        chat_type=ChatType.PRIVATE
    )

    dp.register_message_handler(
        user.unlink_user,
        commands=['unlink'],
        chat_type=ChatType.PRIVATE
    )

    dp.register_message_handler(
        user.update_user_name,
        commands=['name']
    )

    dp.register_message_handler(
        user.update_user_style,
        commands=['style']
    )

    dp.register_message_handler(
        user.update_user_color,
        commands=['color']
    )

    dp.register_message_handler(
        user.update_user_accent,
        commands=['accent']
    )

    dp.register_message_handler(
        user.send_now_playing,
        commands=['now']
    )

    dp.register_message_handler(
        user.send_top_chart,
        commands=['top']
    )

