from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_get_link_keyboard(referral_link: str):
    # Формируем специальную ссылку для кнопки
    msg_url = f"tg://msg_url?url={referral_link}&text="
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Отправить друзьям", 
                    url=msg_url 
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
    return keyboard