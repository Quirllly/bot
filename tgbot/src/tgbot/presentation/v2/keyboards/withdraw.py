from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_withdraw_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="15 ⭐️ (🧸)", callback_data="gift_15_1"),
                InlineKeyboardButton(text="15 ⭐️ (💝)", callback_data="gift_15_2")
            ],
            [
                InlineKeyboardButton(text="25 ⭐️ (🌹)", callback_data="gift_25_1"),
                InlineKeyboardButton(text="25 ⭐️ (🎁)", callback_data="gift_25_2")
            ],
            [
                InlineKeyboardButton(text="50 ⭐️ (🍾)", callback_data="gift_50_1"),
                InlineKeyboardButton(text="50 ⭐️ (💐)", callback_data="gift_50_2")
            ],
            [
                InlineKeyboardButton(text="50 ⭐️ (🚀)", callback_data="gift_50_3"),
                InlineKeyboardButton(text="50 ⭐️ (🎂)", callback_data="gift_50_4")
            ],
            [
                InlineKeyboardButton(text="100 ⭐️ (🏆)", callback_data="gift_100_1"),
                InlineKeyboardButton(text="100 ⭐️ (💍)", callback_data="gift_100_2")
            ],
            [
                InlineKeyboardButton(text="100 ⭐️ (💎)", callback_data="gift_100_3")
            ],
            [
                InlineKeyboardButton(text="Telegram Premium 6мес. (1700 ⭐️)", callback_data="gift_premium")
            ],
            [
                InlineKeyboardButton(text="⬅️ В главное меню", callback_data="main_menu")
            ],
        ]
    )
    return keyboard