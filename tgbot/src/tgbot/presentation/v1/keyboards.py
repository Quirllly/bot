from typing import Sequence

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters.callback_data import CallbackData

from tgbot.application import Sponsor, Task


def get_main_keyboard():
    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Заработать звезды ✨")],
            [
                KeyboardButton(text="Задания 📚"),
                KeyboardButton(text="Профиль 👤"),
                KeyboardButton(text="Рейтинг 📊"),
            ],
            [
                KeyboardButton(text="Отзывы 📗"),
                KeyboardButton(text="Информация 📚"),
                KeyboardButton(text="Инструкция 📕"),
            ],
            [KeyboardButton(text="Вывести звезды ✨")],
        ],
        resize_keyboard=True,
    )

    return menu_keyboard


def get_initial_keyboard(sponsors: Sequence[Sponsor]):
    keyboard = []
    for i in range(len(sponsors)):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"Спонсор {i + 1}",
                    url=sponsors[i].link,
                )
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="Проверить подписку", callback_data="check_subscription"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


class TaskCallback(CallbackData, prefix="task"):
    tg_id: int


def get_subscribe_task_keyboard(task: Task):
    keyboard = []
    keyboard.append(
        [
            InlineKeyboardButton(
                text=f"Канал спонсора",
                url=task.link,
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="Проверить подписку",
                callback_data=TaskCallback(tg_id=int(task.tg_id)).pack(),
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_gain_stars_keyboard():
    gain_stars_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ежедневный бонус 🎁")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )

    return gain_stars_keyboard


def get_bonus_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ежедневный бонус 🎁",
                    callback_data="get_bonus",
                )
            ]
        ]
    )

    return keyboard


def get_reviews_keyboard(url: str):
    reviews_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Перейти на канал",
                    url=url,
                )
            ]
        ]
    )

    return reviews_keyboard


def get_profile_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ввести промокод")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )

    return keyboard


def get_promo_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )

    return keyboard


def get_rating_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="За 24 часа",
                    callback_data="day_top",
                )
            ]
        ]
    )
    return keyboard


def get_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )


def get_daily_bonus_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Забрать бонус 🎁",
                    callback_data="take_daily_bonus",
                )
            ]
        ]
    )

    return keyboard
