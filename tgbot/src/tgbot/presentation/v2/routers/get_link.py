from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.application import UserGateway
from tgbot.presentation.v2.keyboards import (
    get_get_link_keyboard,
)
from tgbot.presentation.v2.subscribe_check import check_with_answer

get_link_router = Router()


@get_link_router.callback_query(F.data == "get_link")
@inject
async def get_daily_bonus(
    callback: CallbackQuery, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(
        bot=bot,
        message=callback.message,
        user_tg_id=callback.from_user.id,
        session=session,
    ):
        return
    user_gateway = UserGateway(session)
    user = await user_gateway.by_tg_id(callback.from_user.id)
    await callback.message.delete()
    referral_link = f"https://t.me/{(await bot.get_me()).username}?start={user.referral_code}"
    await callback.message.answer_animation(
        animation="CgACAgIAAxkBAAIJ92fGGn4_RwXUCWAhf9cpTvfuP-VzAALvagAC-S7ISZjgJ57sv6oYNgQ",  # замените на нужный file_id гифки
        caption="<b>🎉Приглашай друзей и получай по 3⭐️ от Патрика за каждого, кто активирует бота по твоей ссылке!</b>\n"
                "🔗 <b>Твоя личная ссылка</b> (нажми чтобы скопировать):\n"
                f'<code>{referral_link}</code>\n\n'
                "🚀 <b>Как набрать много переходов по ссылке?</b>\n"
                "<blockquote> • Отправь её друзьям в личные сообщения 👥   \n"
                "• Поделись ссылкой в истории в своем ТГ или в своем Telegram канале 📱\n"
                "• Оставь её в комментариях или чатах 🗨  \n"
                "• Распространяй ссылку в соцсетях: TikTok, Instagram, WhatsApp и других 🌍 </blockquote>",
        reply_markup=get_get_link_keyboard(referral_link),
        parse_mode="HTML",
    )
    