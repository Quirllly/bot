from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_mini_games_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ставка 0.5⭐️",
                    callback_data=BetCallback(amount=0.5).pack(),
                ),
                InlineKeyboardButton(
                    text="Ставка 1⭐️", callback_data=BetCallback(amount=1).pack()
                ),
                InlineKeyboardButton(
                    text="Ставка 2⭐️", callback_data=BetCallback(amount=2).pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Ставка 3⭐️", callback_data=BetCallback(amount=3).pack()
                ),
                InlineKeyboardButton(
                    text="Ставка 5⭐️", callback_data=BetCallback(amount=5).pack()
                ),
                InlineKeyboardButton(
                    text="Ставка 10⭐️",
                    callback_data=BetCallback(amount=10).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В главное меню", callback_data="main_menu"
                ),
            ],
        ],
    )
    return keyboard


class BetCallback(CallbackData, prefix="bet"):
    amount: float
