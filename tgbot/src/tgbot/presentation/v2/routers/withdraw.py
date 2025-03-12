from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.application import UserGateway,WithdrawGateway
from tgbot.presentation.v2.keyboards import (
    get_withdraw_keyboard,
)
from tgbot.presentation.v2.subscribe_check import check_with_answer

withdraw_router = Router()


@withdraw_router.callback_query(F.data == "change_stars")
@inject
async def get_daily_bonus1(
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
        animation="CgACAgIAAxkBAAIKFmfGOqVBMesgMlxEJmG8mpD4TkoCAAKgbAACprThScsBSslQA5k5NgQ", 
        caption=f'<b>💰Баланс: </b>{user.balance}⭐️\n'
                "<b>‼️Для вывода требуется:</b>\n"
                f'— минимум 5 приглашенных друзей, активировавших бота\n'
                "— Быть подписанным на наш канал\n\n"
                "<b>Выбери количество звезд и подарок, которым ты хочешь их получить:</b>",
        reply_markup=get_withdraw_keyboard(),
        parse_mode="HTML",
    )


@withdraw_router.callback_query(F.data.startswith("gift_"))
@inject
async def handle_gift_selection(
    callback: CallbackQuery,
    session: FromDishka[AsyncSession],
    bot: Bot
):
    if not await check_with_answer(
        bot=bot,
        message=callback.message,
        user_tg_id=callback.from_user.id,
        session=session,
    ):
        return

    try:
        user_gateway = UserGateway(session)
        withdraw_gateway = WithdrawGateway(session)
        # Получаем пользователя
        user = await user_gateway.by_tg_id(callback.from_user.id)
        
        # Парсим данные
        data = callback.data
        if data == "gift_premium":
            amount = 1700.0
            gift_type = "premium"
        else:
            _, amount_part, gift_num = data.split('_')
            amount = float(amount_part)
            gift_type = f"{amount_part}_{gift_num}"

        # Проверяем условия
        if user.balance < amount:
            await callback.answer("❌ Недостаточно звезд для вывода!")
            return

        if user.amount_of_referrals < 5:
            await callback.answer("❌ Нужно минимум 5 приглашенных друзей!")
            return

        if await withdraw_gateway.has_pending_requests(user.id):
            await callback.answer("❌ У вас уже есть активная заявка!")
            return

        # Создаем запрос и списываем средства

        await withdraw_gateway.create_request(
                user_id=user.id,
                amount=amount,
                gift_type=gift_type
            )
        user.balance -= amount
        await session.commit()

        await callback.answer(
            "🎉 Заявка на вывод принята! Ожидайте подтверждения.",
            show_alert=True
        )
    except ValueError:
        await callback.answer("❌ Ошибка в формате запроса!")
    except Exception as e:
        print(e)
        await session.rollback()
        await callback.answer("❌ Произошла ошибка при обработке запроса!")