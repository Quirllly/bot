from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.presentation.v2.keyboards import get_reviews_keyboard
from tgbot.presentation.v2.subscribe_check import check_with_answer

reviews_router = Router()


@reviews_router.callback_query(F.data == "reviews")
@inject
async def reviews(
    callback: CallbackQuery, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(
        bot=bot,
        message=callback.message,
        user_tg_id=callback.from_user.id,
        session=session,
    ):
        return

    await callback.message.edit_text(
        text="отзывы в канале @channel_name",
        reply_markup=get_reviews_keyboard(),
    )
