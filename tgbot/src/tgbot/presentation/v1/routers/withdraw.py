from aiogram import Router, Bot, F
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.application import Metadata
from tgbot.presentation.v1.shit import check_with_answer

withdraw_router = Router()


@withdraw_router.message(F.text == "Вывести звезды ✨")
@inject
async def withdraw_stars(
    message: Message, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    withdraw = await session.scalar(
        select(Metadata).where(Metadata.name == "Withdraw")
    )

    await message.answer(withdraw.data["text"])
