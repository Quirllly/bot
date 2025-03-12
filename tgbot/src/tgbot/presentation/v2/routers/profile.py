from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery  # Импорт Message добавлен
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dishka.integrations.aiogram import FromDishka, inject
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.application import UserGateway,PromoGateway
from tgbot.presentation.v2.keyboards import get_profile_keyboard,get_faq_keyboard
from tgbot.presentation.v2.subscribe_check import check_with_answer
from tgbot.application.postgres.models import Promocode, PromocodeType,UserPromocode
from sqlalchemy import select
profile_router = Router()


@profile_router.callback_query(F.data == "profile")
@inject
async def profile(
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
    print(callback.from_user)
    await callback.message.delete()
    await callback.message.answer_animation(
        animation="CgACAgIAAxkBAAIKV2fGRe1ERmBAmZMD_FMSj9rpNLTkAAJ6agACprThSXQUewG4dhmzNgQ", 
        caption=f"""
                    <b>✨ Профиль</b>
──────────────
<b>👤 Имя: {callback.from_user.first_name}</b>
<b>🆔 ID: {callback.from_user.id}</b>
──────────────
👥 Всего друзей: {user.amount_of_referrals}
✅ Активировали бота: {user.amount_of_referrals}
💰 Баланс {user.balance}

⁉️ Как получить ежедневный бонус?
<blockquote>Поставь свою личную ссылку на бота в описание своего тг аккаунта, и получай за это +1⭐️ каждый день.</blockquote>

⬇️ <i> Используй кнопки ниже, чтобы ввести промокод, или получить ежедневный бонус.</i>
                    """,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML",
    )


@profile_router.callback_query(F.data == "daily")
@inject
async def daily_bonus(
    callback: CallbackQuery, 
    session: FromDishka[AsyncSession], 
    bot: Bot
):
    user_gateway = UserGateway(session)
    user = await user_gateway.by_tg_id(callback.from_user.id)
    
    # Проверка кулдауна
    if user.last_daily_bonus and (datetime.now() - user.last_daily_bonus) < timedelta(hours=24):
        await callback.answer("❌ Бонус можно получить раз в 24 часа!", show_alert=True)
        return
    
    referral_link = f"https://t.me/{(await bot.get_me()).username}?start={user.referral_code}"
    chat = await bot.get_chat(callback.from_user.id)
    user_bio  = chat.bio if chat.bio else "Био не найдено"
    print(f"User Info: {chat}")
    if referral_link in user_bio: 
        user.balance += 1
        user.last_daily_bonus = datetime.now()
        await session.commit()
        await callback.answer("✅Ты получил ежедневный бонус в размере 1⭐️", show_alert=True)
    else:
        await callback.answer(
            f"❌ Сначала поставь свою личную ссылку в описание профиля или измени настройки конфиденциальности",
            show_alert=True,
            parse_mode="HTML"
        )

class PromoCodeState(StatesGroup):
    waiting_for_promo = State()

@profile_router.callback_query(F.data == "promo")
@inject
async def enter_promo_code(
    callback: CallbackQuery,
    session: FromDishka[AsyncSession],
    bot: Bot,
    state: FSMContext
):
    if not await check_with_answer(
        bot=bot,
        message=callback.message,
        user_tg_id=callback.from_user.id,
        session=session,
    ):
        return

    user_gateway = UserGateway(session)
    promocode_gateway = PromoGateway(session)
    user = await user_gateway.by_tg_id(callback.from_user.id)

    await callback.message.delete()
    await callback.message.answer_animation(
        animation="CgACAgIAAxkBAAIKV2fGRe1ERmBAmZMD_FMSj9rpNLTkAAJ6agACprThSXQUewG4dhmzNgQ",
        caption="✨ <i>Для получения звезд на твой баланс введи промокод:</i>\n"
        "<i>Найти промокоды можно в <a href='https://t.me/patrickstarsfarm'>канале</a> и <a href='https://t.me/patrickstarschat'>чате</a></i>",
        reply_markup=get_faq_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(PromoCodeState.waiting_for_promo)

class PromoCodeState(StatesGroup):
    waiting_for_promo = State()

@profile_router.message(PromoCodeState.waiting_for_promo)
@inject
async def process_promo_code(
    message: Message,
    state: FSMContext,
    session: FromDishka[AsyncSession],
    bot: Bot,
):
    if not await check_with_answer(
        bot=bot,
        message=message,
        user_tg_id=message.from_user.id,
        session=session,
    ):
        return

    user_gateway = UserGateway(session)
    promo_gateway = PromoGateway(session)
    user = await user_gateway.by_tg_id(message.from_user.id)
    promo_code = message.text.strip()
    
    promocode = await promo_gateway.get_valid_promo(promo_code)
    if not promocode:
        await message.answer("❌ Промокод не действителен или закончились использования", show_alert=True)
        await state.clear()
        return

    if await promo_gateway.is_promo_used(user.id, promocode.id):
        await message.answer("🚫 Ты уже активировал(а) этот промокод", show_alert=True)
        await state.clear()
        return

    if not await promo_gateway.can_use_promo(user, promocode):
        await message.answer(
            f"📛 Для активации необходимо {promocode.required_referrals} друга", show_alert=True
        )
        await state.clear()
        return

    try:
        await promo_gateway.activate_promo(user, promocode)
        await message.answer(
            f"✅ Промокод успешно активирован!\n"
            f"Тебе начислено: {promocode.reward} звезд⭐️\n",
            show_alert=True,
        )
    except Exception as e:
        print(f"⚠️ Ошибка: {str(e)}")
    finally:
        await state.clear()
