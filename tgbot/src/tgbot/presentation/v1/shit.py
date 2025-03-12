from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

from tgbot.application import Sponsor, User
from tgbot.presentation.v1.keyboards import get_initial_keyboard


async def check_with_answer(
    *,
    bot: Bot,
    message: Message,
    session: AsyncSession,
) -> bool:
    sponsors = (await session.scalars(select(Sponsor))).all()
    user = await session.scalar(
        select(User).where(User.tg_id == str(message.from_user.id))
    )

    if user and user.username != message.from_user.first_name:
        user.username = message.from_user.first_name
        await session.commit()
    if (
        await check_subscription_to_sponsors(
            user_tg_id=message.from_user.id, bot=bot, sponsors=sponsors
        )
    ) is False:
        await message.answer(
            "❌ Вы не подписаны на все каналы! Подпишитесь и попробуйте снова.",
            reply_markup=get_initial_keyboard(sponsors),
        )
        return False

    return True


async def check_with_answer_for_callbacks(
    *,
    bot: Bot,
    message: Message,
    user_tg_id: int,
    session: AsyncSession,
) -> bool:
    sponsors = (await session.scalars(select(Sponsor))).all()

    if not await check_subscription_to_sponsors(
        user_tg_id=user_tg_id, bot=bot, sponsors=sponsors
    ):
        await message.answer(
            "❌ Вы не подписаны на все каналы! Подпишитесь и попробуйте снова.",
            reply_markup=get_initial_keyboard(sponsors),
        )
        return False

    return True


async def check_subscription_to_sponsors(
    *,
    user_tg_id: int,
    bot: Bot,
    sponsors: Sequence[AsyncSession],
) -> bool:
    for sponsor in sponsors:
        if not await check_subscription(
            user_tg_id=user_tg_id, channel_id=sponsor.tg_id, bot=bot
        ):
            return False

    return True


async def check_subscription(*, user_tg_id: int, channel_id: int, bot: Bot):
    chat_member = await bot.get_chat_member(channel_id, user_tg_id)

    return chat_member.status not in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.KICKED,
    )


async def send_notification(chat_id: str, bot: Bot, message: str) -> None:
    await bot.send_message(chat_id, message)
