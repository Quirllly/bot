from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.application import UserGateway
from tgbot.presentation.v2.keyboards import (
    get_boost_keyboard,
    get_main_keyboard
)
from tgbot.presentation.v2.subscribe_check import check_with_answer


boost_router = Router()


@boost_router.callback_query(F.data == "boost")
@inject
async def get_faq(
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

    await callback.message.answer_animation(
            animation="CgACAgIAAxkBAAIKRmfGRMQBJRCbZKoEbQultiaonLjDAAJLZAAC-S7ISYpppqgYzcmnNgQ",
            caption=f"""
        <b>🚀 Пробусти свой доход за 300 ⭐ с твоего баланса</b>

⭐ Множитель x2 к кликам на 7 дней.
🤝 Множитель x1.5 за друзей на 7 дней.

<b>Баланс: {user.balance}</b>
        """,
        reply_markup=get_boost_keyboard(),
        parse_mode="HTML",
    )


@boost_router.callback_query(F.data == "buy_boost")
@inject
async def get_faq(
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

    one_week_ago = datetime.now() - timedelta(weeks=1)
    if user.boost_timestamp and user.boost_timestamp > one_week_ago:
        await callback.answer(
            text="❌У вас уже активирован boost",
            show_alert=True,
        )
    else:
        if user.balance >= 300:
            user.balance -= 300
            user.boost_timestamp = datetime.now()
            await session.commit()
            await callback.answer(
                text="✅Ты успешно активировал буст",
                show_alert=True,
            )
        else:
            await callback.answer(
                text="❌У тебя недостаточно звезд на балансе",
                show_alert=True,
            )
    
    await callback.message.edit_text(
        "⬅️ В главное меню",
        reply_markup=get_main_keyboard()
    )
