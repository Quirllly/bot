from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.application import UserGateway
from tgbot.presentation.v1.keyboards import (
    get_main_keyboard,
    get_rating_keyboard,
)
from tgbot.presentation.v1.shit import (
    check_with_answer,
    check_with_answer_for_callbacks,
)


rating_router = Router()


@rating_router.message(F.text == "Рейтинг 📊")
@inject
async def rating(
    message: Message, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    user_gateway = UserGateway(session)
    users = await user_gateway.top_referrals_all_time()
    ans = ""
    for user in users:
        ans += f"{user.username} - {user.amount_of_referrals} рефералов\n"

    await message.answer(ans, reply_markup=get_rating_keyboard())


@rating_router.callback_query(F.data == "day_top")
@inject
async def check_user_subscription_callback_answer(
    callback: CallbackQuery, bot: Bot, session: FromDishka[AsyncSession]
):
    if not await check_with_answer_for_callbacks(
        bot=bot,
        message=callback.message,
        session=session,
        user_tg_id=callback.from_user.id,
    ):
        return

    user_gateway = UserGateway(session)
    users = await user_gateway.top_referrals_last_day()
    ans = ""
    for user, new_refs in users:
        ans += f"{user.username} - {new_refs} новых рефералов\n"

    await callback.message.answer(
        ans if ans else "Нет новых рефералов за последние 24 часа",
        reply_markup=get_main_keyboard(),
    )
