from random import random

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.application import UserGateway
from tgbot.presentation.v2.keyboards import (
    get_mini_games_keyboard,
    BetCallback,
)
from tgbot.presentation.v2.subscribe_check import check_with_answer


mini_games_router = Router()


@mini_games_router.callback_query(F.data == "mini_games")
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
        animation="CgACAgIAAxkBAAIKH2fGPMiHK7FGoE0tGqbyy26laebxAAKhagAC-S7ISaP7n8DvgmhDNgQ", 
        caption=f'🔔 Ты попал в  игру "Всё или ничего". Выбери ставку и удвой сумму! 🍀 \n💰 <b>Баланс: {user.balance:.2f}⭐️</b>  \n📊 <b>Онлайн статистика выигрышей</b>: @patrickstars_game  ⭐️',
        reply_markup=get_mini_games_keyboard(),
        parse_mode="HTML",
    )


from aiogram.utils.markdown import hbold
from random import random


@mini_games_router.callback_query(BetCallback.filter())
@inject
async def get_stavka_keyboard(
    callback: CallbackQuery,
    session: FromDishka[AsyncSession],
    bot: Bot,
    callback_data: BetCallback,
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

    if user.balance < callback_data.amount:
        await callback.answer(
            "У вас недостаточно звезд для ставки", show_alert=True
        )
        return

    # Устанавливаем вероятность выигрыша
    if callback_data.amount <= 3:
        chance = 0.45
    elif callback_data.amount == 5:
        chance = 0.4
    else:
        chance = 0.35

    if random() <= chance:
        winnings = callback_data.amount * 2
        user.balance += callback_data.amount
        user.earned += callback_data.amount
        await callback.answer(
            f"🎉 Поздравляю, ты выиграл(а): {winnings} звёзд⭐️ Отличный результат — не останавливайся, попробуй ещё раз! 🚀",
            show_alert=True,
        )

        channel_id = "@patrickstars_game"
        game_result = (
            f"🎉 Поздравляем! 🏆\n\n"
            f"Пользователь {hbold(user.username)} (ID: {user.tg_id})\n"
            f"выиграл {winnings}⭐️ на ставке {callback_data.amount}⭐️ 🎲\n\n"
            f"🚀 Просто потрясающий выигрыш! 🏆🌟 🎉"
        )

        await bot.send_message(channel_id, game_result, parse_mode="HTML")

    else:
        user.balance -= callback_data.amount
        await callback.answer(
            "😕 Неудача, не расстраивайся, надеюсь в следующий раз тебе повезет 🙏",
            show_alert=True,
        )
    await callback.message.delete()
    await callback.message.answer_animation(
        animation="CgACAgIAAxkBAAIKH2fGPMiHK7FGoE0tGqbyy26laebxAAKhagAC-S7ISaP7n8DvgmhDNgQ", 
        caption=f'🔔 Ты попал в  игру <b>"Всё или ничего".</b> Выбери ставку и удвой сумму! \n\n💰<b>Баланс: {user.balance:.2f}⭐️</b> \n\n📊 <b>Онлайн статистика выигрышей</b>: @patrickstars_game',
        reply_markup=get_mini_games_keyboard(),
        parse_mode="HTML",
    )

    await session.commit()
