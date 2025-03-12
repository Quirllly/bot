from datetime import date, timedelta, datetime

from dishka.integrations.aiogram import inject, FromDishka

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject

from tgbot.presentation.v1.keyboards import (
    get_main_keyboard,
    get_initial_keyboard,
)
from tgbot.presentation.v1.shit import (
    check_with_answer_for_callbacks,
    send_notification,
)
from tgbot.application import User, UserGateway, SponsorGateway

start_router = Router()


@start_router.message(CommandStart())
@inject
async def start_handler(
    message: Message, command: CommandObject, session: FromDishka[AsyncSession]
):
    user_gateway = UserGateway(session)
    sponsor_gateway = SponsorGateway(session)
    sponsors = await sponsor_gateway.all_sponsors()
    user = await user_gateway.by_tg_id(message.from_user.id)

    if not user:
        referral_code = command.args
        referrer = None
        if referral_code:
            referrer = await user_gateway.by_referral_code(referral_code)

        user = User(
            tg_id=str(message.from_user.id),
            promo=False,
            daily_bonus=date.today() - timedelta(days=1),
            referrer=referrer.id if referrer else None,
            referral_code=str(message.from_user.id),
            balance=0,
            earned=0,
            verify_timestamp=None,
            username=message.from_user.first_name,
        )

        session.add(user)
        await session.commit()

    await message.answer(
        text="Вам необходимо подписаться на каналы спонсоров, чтобы пользоваться ботом.",
        reply_markup=get_initial_keyboard(sponsors),
    )


@start_router.callback_query(F.data == "check_subscription")
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
    user_tg_id = callback.from_user.id
    user_gateway = UserGateway(session)
    user = await user_gateway.by_tg_id(user_tg_id)

    if not user.verify_timestamp:
        user.verify_timestamp = datetime.now()
        if user.referrer is not None:
            referrer = await session.scalar(
                select(User).where(User.id == str(user.referrer))
            )
            if referrer:
                referrer.balance += 2.5
                referrer.earned += 2.5
                referrer.amount_of_referrals += 1
                await send_notification(
                    chat_id=referrer.tg_id,
                    message=f"По вашей реферальной ссылке зарегестрирован пользователь, вам начислена награда в размере 2.5 ✨",
                    bot=bot,
                )

        await session.commit()

    await callback.message.answer(
        "✅ Вы подписаны на все каналы!", reply_markup=get_main_keyboard()
    )


# @start_router.message()
# async def handle_forwarded_message(message: Message):
#     if message.forward_from_chat:
#         chat = message.forward_from_chat
#         tg_id = chat.id
#         chat_title = chat.title
#         await message.reply(f"ID канала: `{tg_id}`\nНазвание канала: `{chat_title}`", parse_mode="Markdown")
#     else:
#         await message.reply("Пожалуйста, пересылайте сообщения из канала.")
