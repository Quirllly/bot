from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_rating_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="main_menu")],
        ],
    )
    return keyboard
