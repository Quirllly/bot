from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.presentation.v2.subscribe_check import check_with_answer
from tgbot.application import UserGateway


farm_stars_router = Router()


@farm_stars_router.callback_query(F.data == "farm")
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
    cooldown_time = timedelta(minutes=10)

    if user.last_click_timestamp:
        time_diff = datetime.now() - user.last_click_timestamp
        if time_diff < cooldown_time:
            remaining_time = cooldown_time - time_diff
            minutes = remaining_time.seconds // 60
            seconds = remaining_time.seconds % 60
            await callback.answer(
                f"Подождите {minutes} мин {seconds} сек перед следующим кликом ⏳",
                show_alert=True,
            )
            return

    amount_to_add = (
        0.1 * 2
        if user.boost_timestamp > datetime.now() - timedelta(weeks=1)
        else 0.1
    )
    user.balance += amount_to_add
    user.earned += amount_to_add
    user.last_click_timestamp = datetime.now()
    await session.commit()
    await callback.answer(f"Ты получил {amount_to_add}0⭐️", show_alert=True)
