from aiogram.types import (
        InlineKeyboardButton,
        InlineKeyboardMarkup,
    )
from aiogram.filters.callback_data import CallbackData

from tgbot.application import Task


class TaskCallback(CallbackData, prefix="task"):
        tg_id: int


def get_subscribe_task_keyboard(task: Task):
        print(task.id)
        if (task.type == "invite_link"):
                invite_link = task.invite_link
        elif (task.type == "subscription"):
                invite_link = task.invite_link
        elif (task.type == "bot_start"):
                invite_link = "https://t.me/" + task.bot_username
        else:
                print("Error")
        return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Подписаться на канал",
                    url=invite_link
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить подписку",
                    callback_data=TaskCallback(tg_id=task.id).pack()  # Используем правильное имя поля
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )
