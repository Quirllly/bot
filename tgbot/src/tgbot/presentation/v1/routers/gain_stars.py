from datetime import datetime
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.application import UserGateway, MetadataGateway
from tgbot.presentation.v1.keyboards import (
    get_gain_stars_keyboard,
    get_daily_bonus_keyboard,
)
from tgbot.presentation.v1.shit import (
    check_with_answer,
    check_with_answer_for_callbacks,
)


gain_stars_router = Router()


@gain_stars_router.message(F.text == "Заработать звезды ✨")
@inject
async def gain_stars(
    message: Message, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    user_gateway = UserGateway(session=session)
    user = await user_gateway.by_tg_id(message.from_user.id)

    if not user:
        raise Exception()  # почему-то прокидывается хуйня

    await message.answer(
        f"За приглашение друзей по своей ссылке ты будешь получать по 2.5✨\n"
        f"Твоя личная ссылка: https://t.me/{(await bot.get_me()).username}?start={user.referral_code}",
        reply_markup=get_gain_stars_keyboard(),
    )


@gain_stars_router.message(F.text == "Ежедневный бонус 🎁")
@inject
async def get_daily_bonus(
    message: Message, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return
    metadata_gateway = MetadataGateway(session)
    daily_reward_data = (await metadata_gateway.by_name("daily_reward")).data

    await message.answer(
        f"Пригласи {daily_reward_data['people_for_reward']} друзей за 24ч и получи ежедневный бонус в paзмepe {daily_reward_data['reward']}✨",
        reply_markup=get_daily_bonus_keyboard(),
    )


@gain_stars_router.callback_query(F.data == "take_daily_bonus")
@inject
async def take_daily_bonus(
    callback: CallbackQuery, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer_for_callbacks(
        bot=bot,
        message=callback.message,
        session=session,
        user_tg_id=callback.from_user.id,
    ):
        return

    user_gateway = UserGateway(session)
    metadata_gateway = MetadataGateway(session)
    user = await user_gateway.by_tg_id(callback.from_user.id)
    daily_reward_data = (await metadata_gateway.by_name("daily_reward")).data

    last_day_referrals_amount = await user_gateway.last_day_referrals_amount(
        user.tg_id
    )

    today = datetime.now().date()

    if (
        last_day_referrals_amount >= daily_reward_data["people_for_reward"]
        and user.daily_bonus < today
    ):
        user.daily_bonus = today
        user.balance += daily_reward_data["reward"]
        user.earned += daily_reward_data["reward"]
        await callback.answer("Вам начислен ежедневный бонус")
        await session.commit()

    elif last_day_referrals_amount < daily_reward_data["people_for_reward"]:
        await callback.message.answer(
            f"Вам нужно пригласить еще {daily_reward_data['people_for_reward'] - last_day_referrals_amount} пользователей",
            show_alert=True,
        )
    else:
        await callback.message.answer(
            f"Вы уже забирали награду сегодня",
            show_alert=True,
        )
