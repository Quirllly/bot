from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from tgbot.presentation.v2.keyboards import (
    get_main_keyboard,
)
from tgbot.presentation.v2.subscribe_check import check_with_answer

main_router = Router()


@main_router.callback_query(F.data == "main_menu")
@inject
async def back(
    callback: CallbackQuery, session: FromDishka[AsyncSession], bot: Bot
):
    if not await check_with_answer(
        bot=bot,
        message=callback.message,
        user_tg_id=callback.from_user.id,
        session=session,
    ):
        return
    await callback.message.delete()
    await callback.message.answer_animation(
        animation="CgACAgIAAxkBAAIJ42fGFrVZO7JsCET2dD52ZZdULq92AAJlagACprThSV6Y0mfWImDfNgQ",  # замените на нужный file_id гифки
        caption="1️⃣ Получи свою личную ссылку — жми «⭐️ Заработать звезды»\n"
                "2️⃣ Приглашай друзей — 3⭐️ за каждого!\n\n"
                "✅ Дополнительно:\n"
                "<blockquote> — Ежедневные награды и промокоды (Профиль) \n"
                "— Выполняй задания\n"
                "— Испытай удачу в мини-играх\n"
                "— Участвуй в конкурсе на топ </blockquote>",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML",
    )