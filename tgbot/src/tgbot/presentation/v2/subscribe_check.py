from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

from tgbot.application import (
    User,
    Sponsor,
    SponsorGateway,
    UserGateway,
    SubscribeGateway,
)
from tgbot.presentation.v1.keyboards import get_initial_keyboard


async def check_with_answer(
    *,
    bot: Bot,
    message: Message,
    user_tg_id: int,
    session: AsyncSession,
) -> bool:
    sponsor_gateway = SponsorGateway(session)
    user_gateway = UserGateway(session)
    sponsors = await sponsor_gateway.all_sponsors()
    user = await user_gateway.by_tg_id(user_tg_id)

    if not await check_subscription_to_sponsors(
        user=user, bot=bot, sponsors=sponsors, session=session
    ):
        await message.edit_text(
            "❌ Вы не подписаны на все каналы! Подпишитесь и попробуйте снова.",
            reply_markup=get_initial_keyboard(sponsors),
        )
        return False

    return True


async def check_subscription_to_sponsors(
    *,
    user: User,
    bot: Bot,
    sponsors: Sequence[Sponsor],
    session: AsyncSession,
) -> bool:
    subscribe_gateway = SubscribeGateway(session=session)

    for sponsor in sponsors:
        if (
            await subscribe_gateway.by_user_id_and_sponsor_id(
                user_id=user.id, sponsor_id=sponsor.id
            )
            is None
        ):
            if await check_subscription(
                user_tg_id=user.tg_id, channel_id=sponsor.tg_id, bot=bot
            ):
                await subscribe_gateway.add_subscribe(
                    user_id=user.id, sponsor_id=sponsor.id
                )

            else:
                return False

    return True


async def check_subscription(*, user_tg_id: int, channel_id: int, bot: Bot):
    chat_member = await bot.get_chat_member(channel_id, user_tg_id)

    return chat_member.status not in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.KICKED,
    )


# async def send_notification(chat_id: str, bot: Bot, message: str) -> None:
#     await bot.send_message(chat_id, message)
