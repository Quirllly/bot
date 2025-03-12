from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.application import UserGateway, Promocode, User
from tgbot.presentation.v1.shit import check_with_answer
from tgbot.presentation.v1.keyboards import (
    get_profile_keyboard,
    get_main_keyboard,
    get_back_keyboard,
)

profile_router = Router()


@profile_router.message(F.text == "Профиль 👤")
@inject
async def profile(
    message: Message, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    gateway = UserGateway(session=session)

    user = await gateway.by_tg_id(message.from_user.id)

    if not user:
        raise Exception()  # TODO кидает сюда если удалить юзера и кликнуть снова на клаву

    await message.answer(
        f"ник: @{message.from_user.username}\n"
        f"друзей приглашено: {user.amount_of_referrals}\n"
        f"заработано звезд: {user.earned}\n"
        f"баланс: {user.balance}",
        reply_markup=get_profile_keyboard(),
    )


class PromoCodeState(StatesGroup):
    waiting_for_promo = State()


@profile_router.message(F.text == "Ввести промокод")
@inject
async def enter_promo_code(
    message: Message,
    session: FromDishka[AsyncSession],
    bot: Bot,
    state: FSMContext,
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    user_gateway = UserGateway(session=session)
    user = await user_gateway.by_tg_id(message.from_user.id)

    if user.promo:
        await message.answer(
            "Вы уже вводили промокод", reply_markup=get_main_keyboard()
        )

    else:
        await message.answer(
            "Введите ваш промокод", reply_markup=get_back_keyboard()
        )
        await state.set_state(PromoCodeState.waiting_for_promo)


@profile_router.message(PromoCodeState.waiting_for_promo)
@inject
async def process_promo_code(
    message: Message,
    state: FSMContext,
    session: FromDishka[AsyncSession],
    bot: Bot,
):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    # Если текст сообщения отсутствует.
    if not message.text:
        await message.answer("Некорректное сообщение. Попробуйте ещё раз.")
        return

    # Обработка команды "Назад"
    if message.text == "Назад":
        await message.answer(
            "🔝 Главное Меню", reply_markup=get_main_keyboard()
        )
        await state.clear()
        return

    # Ищем промокод в базе данных
    promo = await session.scalar(
        select(Promocode).where(Promocode.name == message.text)
    )
    if not promo:
        await message.answer("Такого промокода не существует")
        return

    # Проверяем, есть ли оставшиеся использования промокода
    if promo.remaining_usages <= 0:
        await message.answer("Этот промокод больше недействителен")
        return

    # Обновляем данные промокода
    promo.remaining_usages -= 1

    # Ищем пользователя по его Telegram ID
    user = await session.scalar(
        select(User).where(User.tg_id == str(message.from_user.id))
    )
    if not user:
        await message.answer("Пользователь не найден")
        return

    # Начисляем вознаграждение пользователю
    user.balance += promo.reward
    user.earned += promo.reward
    user.promo = True

    # Фиксируем изменения в базе
    await session.commit()
    await state.clear()

    # Сообщаем пользователю об успешном применении промокода
    await message.answer(
        f"Вы ввели промокод: {message.text}\nПромокод принят!\nВам начислено - {promo.reward} звед",
        reply_markup=get_main_keyboard(),
    )
