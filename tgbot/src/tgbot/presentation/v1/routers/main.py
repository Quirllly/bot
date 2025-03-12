from aiogram import Router, F, Bot
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession
from dishka.integrations.aiogram import inject, FromDishka

from tgbot.presentation.v1.keyboards import (
    get_reviews_keyboard,
    get_main_keyboard,
)
from tgbot.application import MetadataGateway
from tgbot.presentation.v1.shit import (
    check_with_answer,
)

main_router = Router()


@main_router.message(F.text == "Отзывы 📗")
@inject
async def reviews_handler(
    message: Message, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    metadata_gateway = MetadataGateway(session=session)
    reviews = await metadata_gateway.by_name("Reviews")

    await message.answer(
        reviews.data["text"],
        reply_markup=get_reviews_keyboard(reviews.data["link"]),
    )


@main_router.message(F.text == "Информация 📚")
@inject
async def information_handler(
    message: Message, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return
    metadata_gateway = MetadataGateway(session=session)
    information = await metadata_gateway.by_name("Information")

    await message.answer(information.data["text"])


@main_router.message(F.text == "Инструкция 📕")
@inject
async def instruction(
    message: Message, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    metadata_gateway = MetadataGateway(session=session)
    instruction = await metadata_gateway.by_name("Instruction")

    await message.answer(instruction.data["text"])


@main_router.message(F.text == "Назад")
@inject
async def back(message: Message, session: FromDishka[AsyncSession], bot: Bot):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return
    await message.answer(
        text="🔝 Главное Меню",
        reply_markup=get_main_keyboard(),
    )
