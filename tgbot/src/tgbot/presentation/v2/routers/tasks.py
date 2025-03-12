from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject
from aiogram.types import (
        InlineKeyboardButton,
        InlineKeyboardMarkup,
    )
from tgbot.presentation.v2.keyboards import (
    get_main_keyboard,
    get_subscribe_task_keyboard,
    TaskCallback,
)
from tgbot.presentation.v2.subscribe_check import (
    check_with_answer,
    check_subscription,
)
from uuid import UUID
from tgbot.application import UserGateway, TaskGateway, UserTaskGateway
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ChatJoinRequest
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka, inject
from tgbot.application.postgres.models  import Task, User, UserTaskData
from tgbot.application.postgres.services import TaskChecker

tasks_router = Router()

@tasks_router.chat_join_request()
@inject
async def handle_invite(
    request: ChatJoinRequest,
    session: FromDishka[AsyncSession],
):
    user_gateway = UserGateway(session)
    user = await user_gateway.by_tg_id(request.from_user.id)
    user_data = await session.get(UserTaskData, user.id) or UserTaskData(user_id=user.id)
    user_data.used_invites.setdefault(str(request.chat.id), []).append(request.invite_link.invite_link)
    await session.commit()

@tasks_router.message(F.text == "/start")
@inject
async def handle_bot_start(
    message: Message,
    session: FromDishka[AsyncSession],

):
    user_gateway = UserGateway(session)
    user = await user_gateway.by_tg_id(message.from_user.id)
    user_data = await session.get(UserTaskData, user.id) or UserTaskData(user_id=user.id)
    bot_username = (await message.bot.get_me()).username
    if bot_username not in user_data.started_bots:
        user_data.started_bots.append(bot_username)
        await session.commit()

@tasks_router.callback_query(F.data.startswith("task1_"))
@inject
async def handle_task(
    callback: CallbackQuery,
    session: FromDishka[AsyncSession],
    bot: Bot,
):
    print(callback.data)  # Для отладки

    try:
        # Извлекаем тип задачи
        task_type = callback.data.split("_", 1)[1]
        task_type = {
            "subscription": "subscription",
            "invite_link": "invite_link",
            "bot_start": "bot_start"
        }.get(task_type, None)

        if task_type is None:
            print(f"Ошибка: Неверный task_type {callback.data}")
            await callback.answer("❌ Ошибка: неизвестный тип задачи.")
            return

        # Логируем тип задачи
        print(f"Тип задачи: {task_type}")

    except (IndexError, ValueError) as e:
        print(f"Ошибка при обработке callback.data: {e}, данные: {callback.data}")
        await callback.answer("❌ Ошибка: некорректный формат задачи.")
        return

    # Работа с БД
    user_gateway = UserGateway(session)
    task_gateway = TaskGateway(session)

    try:
        user = await user_gateway.by_tg_id(callback.from_user.id)

        # Ищем задачу по типу
        task = await task_gateway.get_task_by_type(task_type)

        if not task:
            await callback.answer(f"❌ Задача {task_type} не найдена!")
            return

        await callback.answer(f"✅ Найдена задача: {task.title}")

    except Exception as e:
        print(f"Ошибка при обработке задачи: {e}")
        await callback.answer("❌ Ошибка при обработке задачи.")

@tasks_router.callback_query(F.data == "tasks")
@inject
async def show_tasks(
    callback: CallbackQuery,
    session: FromDishka[AsyncSession]
):
    task_gateway = TaskGateway(session)
    user_gateway = UserGateway(session)
    
    user = await user_gateway.by_tg_id(callback.from_user.id)
    task = await task_gateway.get_next_task(user.id)

    if not task:
        await callback.answer("🎉 Все задания выполнены!", show_alert=True)
        return

    await callback.message.delete()
    await callback.message.answer(
        format_task_message(task),
        reply_markup=get_subscribe_task_keyboard(task)
    )

@tasks_router.callback_query(TaskCallback.filter())
@inject
async def check_task_completion(
    callback: CallbackQuery,
    callback_data: TaskCallback,
    session: FromDishka[AsyncSession],
    bot: Bot,
):
    task_gateway = TaskGateway(session)
    user_gateway = UserGateway(session)
    task_checker = TaskChecker(bot, session)

    try:
        user = await user_gateway.by_tg_id(callback.from_user.id)
        task = await task_gateway.get_task_by_id(callback_data.tg_id)
        print("Проверяем подписку пользователя", user.tg_id, "на канал", task.channel_id)
        
        if not user or not task:
            await callback.answer("❌ Ошибка: пользователь или задача не найдены.")
            return

        print("Проверяем подписку пользователя", user.tg_id, "на канал", task.channel_id)
        is_completed = await task_checker.verify(user.tg_id, task)
        print("Подписка пользователя", user.tg_id, "на канал", task.channel_id, "проверена:", is_completed)
        
        if is_completed:
            # Помечаем задачу как выполненную
            await task_gateway.mark_task_completed(user.id, task.id)
            print("Задача", task.id, "помечена как выполненная")
            
            # Начисляем награду
            user.balance += task.reward
            await session.commit()

            # Удаляем старое сообщение
            await callback.message.delete()

            # Показываем следующую задачу
            next_task = await task_gateway.get_next_task(user.id)
            print("Показываем следующую задачу", next_task)
            
            if next_task:
                # Отправляем новое сообщение с новой задачей
                await callback.message.answer(
                    text=format_task_message(next_task),
                    reply_markup=get_subscribe_task_keyboard(next_task)
                )
                await callback.answer("✅ Задание выполнено! Переходим к следующему.")
            else:
                # Если задач больше нет, отправляем сообщение о завершении
                await callback.message.answer(
                    "🎉 Все задания выполнены!",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(
                                text="🏠 В главное меню",
                                callback_data="main_menu"
                            )]
                        ]
                    )
                )
                await callback.answer("🎉 Все задания выполнены!")
        else:
            await callback.answer("❌ Подписка не найдена. Пожалуйста, подпишитесь сначала.")

    except Exception as e:
        print(f"Error checking task: {e}")
        await callback.answer("⚠️ Произошла ошибка при проверке задания")

def format_task_message(task: Task) -> str:
    return (
        f"✨ Новое задание! ✨\n\n"
        f"• Подпишись на канал ({task.type})\n\n"
        f"Награда: {task.reward}⭐️\n\n"
        "📌 Чтобы получить награду полностью, подпишись и НЕ отписывайся "
        "от канала/группы в течение 3-х дней"
    )