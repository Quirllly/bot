from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.presentation.v2.keyboards import (
    get_faq_keyboard,
)
from tgbot.presentation.v2.subscribe_check import check_with_answer
from tgbot.application import UserGateway

rating_router = Router()
import logging

logger = logging.getLogger(__name__)
@rating_router.callback_query(F.data == "rating")
@inject
async def get_top(
    callback: CallbackQuery, session: FromDishka[AsyncSession], bot: Bot
):
    try:
        logger.info("Начало обработки callback 'rating'")

        if not await check_with_answer(
            bot=bot,
            message=callback.message,
            user_tg_id=callback.from_user.id,
            session=session,
        ):
            logger.warning("Проверка check_with_answer не пройдена")
            return

        user_gateway = UserGateway(session)
        logger.info("Создан UserGateway")

        top_3 = await user_gateway.top_referrals_last_day(3)
        logger.info(f"Топ-3 рефералов за день: {top_3}")

        current_user = await user_gateway.by_tg_id(callback.from_user.id)
        logger.info(f"Текущий пользователь: {current_user}")

        current_user_position = await user_gateway.get_user_position(callback.from_user.id)
        logger.info(f"Текущая позиция пользователя: {current_user_position}")

        # Формируем текст для топ-3
        top_text = "<b>🏆 Топ 3 за день:</b>\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (user, referral_count) in enumerate(top_3):
            top_text += f"{medals[i]} {user.username} | Друзей: {referral_count}\n"

        # Формируем текст с бонусами
        bonus_text = (
            "\n<b>Попади в топ 3 и получи бонус в конце дня:</b>\n"
            "<blockquote>- 1ое место + 100⭐️\n"
            "- 2ое место + 50⭐️\n"
            "- 3е место + 25⭐️</blockquote>"
        )

        # Формируем текст с текущим положением пользователя
        user_position_text = f"<b>✨Сейчас ты на: {current_user_position} месте | Друзей: {current_user.amount_of_referrals}</b>"

        # Объединяем всё в одно сообщение
        message_text = f"{top_text}\n{bonus_text}\n{user_position_text}"
        logger.info(f"Сформирован текст сообщения: {message_text}")

        # Отправляем сообщение с гифкой
        await callback.message.delete()
        logger.info("Сообщение удалено")

        await callback.message.answer_animation(
            animation="CgACAgIAAxkBAAIKJ2fGPqee-ZC3An71F8vRV671eT-MAALxcAAC5yvBSRCUSyNXqFePNgQ",
            caption=message_text,
            reply_markup=get_faq_keyboard(),
            parse_mode="HTML",
        )
        logger.info("Сообщение с гифкой отправлено")

    except Exception as e:
        logger.error(f"Ошибка в get_top: {e}", exc_info=True)