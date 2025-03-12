# presentation/v2/admin.py
# presentation/v2/admin.py
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dishka.integrations.aiogram import FromDishka, inject
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from tgbot.application.postgres.models import (
    Admins, Promocode, PromocodeType, 
    WithdrawalRequest, User, Task, TaskType
)
from tgbot.application import UserGateway, WithdrawGateway, TaskGateway
from sqlalchemy import select
from aiogram.methods import SendGift
from aiogram.methods import GetAvailableGifts

admin_router = Router()


class TaskCreationStates(StatesGroup):
    CHOOSE_TYPE = State()
    ENTER_SUBSCRIPTION = State()
    ENTER_INVITE = State()
    ENTER_BOT_START = State()


class WithdrawStates(StatesGroup):
    VIEWING_REQUESTS = State()
class PromoCreationStates(StatesGroup):
    CHOOSE_TYPE = State()
    ENTER_SIMPLE = State()
    ENTER_REFERRAL = State()
class TaskDeletionStates(StatesGroup):
    CHOOSING_TASK = State()
    CONFIRM_DELETION = State()
def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать промокод", callback_data="create_promo"),
         InlineKeyboardButton(text="🎯 Создать задачу", callback_data="create_task")],
        [InlineKeyboardButton(text="🗑 Удалить задачу", callback_data="delete_task"),
         InlineKeyboardButton(text="📤 Запросы на вывод", callback_data="withdraw_requests")]
    ])

@admin_router.callback_query(F.data == "create_task")
async def create_task_start(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Подписка", callback_data="task_type_subscription")],  # Было: task_type_subscription
        [InlineKeyboardButton(text="🔗 Приглашение", callback_data="task_type_invite_link")],  # Было: task_type_invite_link
        [InlineKeyboardButton(text="🤖 Старт бота", callback_data="task_type_bot_start")],  # Было: task_type_bot_start

        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    await callback.message.edit_text(
        "Выберите тип задачи:",
        reply_markup=keyboard
    )
    await state.set_state(TaskCreationStates.CHOOSE_TYPE)


@admin_router.callback_query(F.data.startswith("task_type_"))
async def process_task_type(callback: CallbackQuery, state: FSMContext):
    task_type = callback.data.split("_")[2]
    await state.update_data(task_type=task_type)
    
    text = ""
    if task_type == "subscription":
        text = (
            "📝 Введите параметры задачи в формате:\n\n"
            "<code>Название|Описание|Награда|ID канала</code>\n\n"
            "Пример:\n"
            "<code>Подписка|Подпишитесь на канал|50.0|@my_channel</code>"
        )
    elif task_type == "invite":
        text = (
            "📝 Введите параметры задачи в формате:\n\n"
            "<code>Название|Описание|Награда|ID чата|Пригласительная ссылка</code>\n\n"
            "Пример:\n"
            "<code>Приглашение|Пригласите 5 друзей|100.0|-10012345|https://t.me/+invite_link</code>"
        )
    elif task_type == "bot":
        text = (
            "📝 Введите параметры задачи в формате:\n\n"
            "<code>Название|Описание|Награда|Ссылку|Токен бота</code>\n\n"
            "Пример:\n"
            "<code>Бот|Запустите бота|150.0|MyBot|123456:ABC-DEF1234ghIkl</code>"
        )
    
    await callback.message.edit_text(text, parse_mode="HTML")

    state_mapping = {
        "subscription": TaskCreationStates.ENTER_SUBSCRIPTION,
        "invite": TaskCreationStates.ENTER_INVITE,
        "bot": TaskCreationStates.ENTER_BOT_START
    }
    await state.set_state(state_mapping[task_type])

@admin_router.message(TaskCreationStates.ENTER_SUBSCRIPTION)
@inject
async def process_subscription_task(
    message: Message, 
    state: FSMContext,
    session: FromDishka[AsyncSession]
):
    try:
        parts = message.text.split("|")
        if len(parts) != 5:
            await message.answer("❌ Ошибка: Неверный формат! Используйте:\n"
                                 "<code>Название|Описание|Награда|Ссылку|ID канала</code>", parse_mode="HTML")
            return

        task = Task(
            type=TaskType.SUBSCRIPTION,
            title=parts[0].strip(),
            description=parts[1].strip(),
            reward=float(parts[2].strip()),
            channel_id=parts[3].strip(),
            invite_link=parts[3].strip(),
            chat_id=parts[4].strip(),
            giphy_url="https://example.com/default.gif"
        )

        session.add(task)
        await session.commit()
        await message.answer(f"✅ Задача 'Подписка' создана: {task.title}!")
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        await state.clear()

@admin_router.callback_query(F.data == "delete_task")
@inject
async def delete_task_start(
    callback: CallbackQuery,
    state: FSMContext,
    session: FromDishka[AsyncSession]
):
    task_gateway = TaskGateway(session)
    tasks = await task_gateway.get_all_tasks()
    
    if not tasks:
        await callback.answer("📭 Список задач пуст!")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *[
            [InlineKeyboardButton(
                text=f"🗑 {task.title} ({task.type})",  # Используем value для enum
                callback_data=f"task_delete_{task.id}"
            )] for task in tasks
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(
        "📋 Выберите задачу для удаления:",
        reply_markup=keyboard
    )
    await state.set_state(TaskDeletionStates.CHOOSING_TASK)

@admin_router.callback_query(F.data.startswith("task_delete_"))
@inject
async def confirm_task_deletion(
    callback: CallbackQuery,
    state: FSMContext,
    session: FromDishka[AsyncSession]
):
    task_id = int(callback.data.split("_")[2])
    task = await TaskGateway(session).get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена!")
        return
    
    await state.update_data(task_id=task_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_deletion")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_deletion")]
    ])
    
    await callback.message.edit_text(
        f"⚠️ Вы уверены, что хотите удалить задачу?\n\n"
        f"Название: {task.title}\n"
        f"Тип: {task.type}\n"
        f"Награда: {task.reward}⭐️",
        reply_markup=keyboard
    )
    await state.set_state(TaskDeletionStates.CONFIRM_DELETION)

@admin_router.callback_query(F.data == "confirm_deletion")
@inject
async def process_task_deletion(
    callback: CallbackQuery,
    state: FSMContext,
    session: FromDishka[AsyncSession]
):
    data = await state.get_data()
    task_id = data.get("task_id")
    
    if not task_id:
        await callback.answer("❌ Ошибка: задача не найдена!")
        return
    
    task = await TaskGateway(session).get_task_by_id(task_id)
    if task:
        await session.delete(task)
        await session.commit()
        await callback.answer("✅ Задача успешно удалена!")
    else:
        await callback.answer("❌ Задача не найдена!")
    
    await state.clear()
    await back_to_admin_panel(callback)

@admin_router.callback_query(F.data == "cancel_deletion")
async def cancel_task_deletion(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🗑 Удаление задачи отменено!",
        reply_markup=get_admin_keyboard()
    )

@admin_router.message(TaskCreationStates.ENTER_INVITE)
@inject
async def process_invite_task(
    message: Message, 
    state: FSMContext,
    session: FromDishka[AsyncSession]
):
    try:
        parts = message.text.split("|")
        if len(parts) != 5:
            await message.answer("❌ Ошибка: Неверный формат! Используйте:\n"
                                 "<code>Название|Описание|Награда|Порядок|ID чата|Пригласительная ссылка</code>", parse_mode="HTML")
            return

        task = Task(
            type=TaskType.INVITE_LINK,
            title=parts[0].strip(),
            description=parts[1].strip(),
            reward=float(parts[2].strip()),
            chat_id=parts[3].strip(),
            invite_link=parts[4].strip(),
            giphy_url="https://example.com/default.gif"
        )

        session.add(task)
        await session.commit()
        await message.answer(f"✅ Задача 'Приглашение' создана: {task.title}!")
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        await state.clear()


@admin_router.message(TaskCreationStates.ENTER_BOT_START)
@inject
async def process_bot_task(
    message: Message, 
    state: FSMContext,
    session: FromDishka[AsyncSession]
):
    try:
        parts = message.text.split("|")
        if len(parts) != 5:
            await message.answer("❌ Ошибка: Неверный формат! Используйте:\n"
                                 "<code>Название|Описание|Награда|Порядок|Юзернейм бота|Токен бота</code>", parse_mode="HTML")
            return

        task = Task(
            type=TaskType.BOT_START,
            title=parts[0].strip(),
            description=parts[1].strip(),
            reward=float(parts[2].strip()),
            bot_username=parts[3].strip(),
            bot_token=parts[4].strip(),
            giphy_url="https://example.com/default.gif"
        )

        session.add(task)
        await session.commit()
        await message.answer(f"✅ Задача 'Старт бота' создана: {task.title}!")
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        await state.clear()

@admin_router.callback_query(F.data == "withdraw_requests")
@inject
async def show_withdraw_requests(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    session: FromDishka[AsyncSession],
):
    withdraw_gateway = WithdrawGateway(session)
    requests = await withdraw_gateway.get_all_pending()
    if not requests:
        await callback.answer("🚫 Нет активных запросов на вывод!")
        return

    await state.update_data(
        request_ids=[str(req.id) for req in requests],
        current_index=0
    )
    await state.set_state(WithdrawStates.VIEWING_REQUESTS)
    await show_current_request(callback.message, state, withdraw_gateway)

async def show_current_request(
    message: Message, 
    state: FSMContext,
    withdraw_gateway: WithdrawGateway
):
    data = await state.get_data()
    request_ids = data['request_ids']
    current_index = data['current_index']
    
    try:
        request = await withdraw_gateway.get_request_by_id(UUID(request_ids[current_index]))
        user = await withdraw_gateway.get_user_by_request(request)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        return

    emoji_mapping = {
        '15_1': '🧸', '15_2': '💝',
        '25_1': '🌹', '25_2': '🎁',
        '50_1': '🍾', '50_2': '💐',
        '50_3': '🚀', '50_4': '🎂',
        '100_1': '🏆', '100_2': '💍',
        '100_3': '💎', 'premium': '👑'
    }

    text = (
        f"✅ Запрос на вывод No: {request.id}\n\n"
        f"Пользователь: @{user.username if user.username else 'нет'} | ID: {user.tg_id}\n"
        f"Количество: {request.amount} {emoji_mapping.get(request.gift_type, '🎁')}\n\n"
        f"Статус: {request.status.capitalize()}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", 
                callback_data=f"withdraw_approve_{request.id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить", 
                callback_data=f"withdraw_reject_{request.id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 Профиль", 
                url=f"tg://user?id={user.tg_id}"
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Пред", callback_data="withdraw_prev"),
            InlineKeyboardButton(text="След ➡️", callback_data="withdraw_next")
        ],
        [
            InlineKeyboardButton(text="⬅️ В админку", callback_data="admin_back")
        ]
    ])

    await message.edit_text(text, reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("withdraw_"))
@inject
async def handle_withdraw_actions(
    callback: CallbackQuery,
    state: FSMContext,
    session: FromDishka[AsyncSession],
    bot: Bot,
):
    action = callback.data.split("_")[1]
    user_gateway = UserGateway(session)
    withdraw_gateway = WithdrawGateway(session)
    
    if action in ["prev", "next"]:
        data = await state.get_data()
        current_index = data['current_index']
        
        if action == "prev" and current_index > 0:
            current_index -= 1
        elif action == "next" and current_index < len(data['request_ids']) - 1:
            current_index += 1
            
        await state.update_data(current_index=current_index)
        await show_current_request(callback.message, state, withdraw_gateway)
        return

    if action in ["approve", "reject"]:
        request_id = UUID(callback.data.split("_")[2])
        request = await withdraw_gateway.get_request_by_id(request_id)
        user = await user_gateway.by_id(request.user_id)

        if action == "approve":
            request.status = "approved"
            await session.commit()
            
            # Отправляем сообщение об одобрении через Aiogram (оповещение в чате)
            await bot.send_message(
                user.tg_id, 
                f"🎉 Ваш запрос на вывод {request.amount}⭐️ одобрен!"
            )
            
            # Отправка подарка через Telethon
            
            await callback.answer("✅ Запрос одобрен!")
        else:
            request.status = "rejected"
            user.balance += request.amount
            await session.commit()
            
            # Оповещение об отклонении через Aiogram
            await bot.send_message(
                user.tg_id, 
                f"❌ Запрос на вывод отклонен. Возвращено {request.amount}⭐️"
            )
            
            await callback.answer("❌ Запрос отклонен!")

        await show_current_request(callback.message, state, withdraw_gateway)


@admin_router.message(F.text == "/admin")
@inject
async def admin_panel(
    message: Message,
    session: FromDishka[AsyncSession],
    bot: Bot
):
    # Проверка через базу данных
    is_admin = await session.scalar(
        select(Admins).where(Admins.user_id == message.from_user.id)
    )
    
    if not is_admin:
        return await message.answer("⛔ Доступ запрещен!")
    
    await message.answer(
        "🛠 Панель администратора:",
        reply_markup=get_admin_keyboard()
    )

@admin_router.callback_query(F.data == "admin_back")
async def back_to_admin_panel(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛠 Панель администратора:",
        reply_markup=get_admin_keyboard()
    )

@admin_router.callback_query(F.data == "create_promo")
async def create_promo_start(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Простой", callback_data="promo_type_simple")],
        [InlineKeyboardButton(text="👥 Реферальный", callback_data="promo_type_referral")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    await callback.message.edit_text(
        "Выберите тип промокода:",
        reply_markup=keyboard
    )
    await state.set_state(PromoCreationStates.CHOOSE_TYPE)

@admin_router.callback_query(F.data.startswith("promo_type_"))
async def process_promo_type(callback: CallbackQuery, state: FSMContext):
    promo_type = callback.data.split("_")[2]
    await state.update_data(promo_type=promo_type.lower())
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    if promo_type == "simple":
        text = ("📝 Введите параметры промокода в формате:\n\n"
                "<code>Название|Награда|Лимит|Срок (часов)</code>\n\n"
                "Пример:\n"
                "<code>SUMMER2024|50|100|24</code>")
    else:
        text = ("📝 Введите параметры промокода в формате:\n\n"
                "<code>Название|Награда|Лимит|Срок (часов)|Требуется рефералов</code>\n\n"
                "Пример:\n"
                "<code>REFBONUS|100|50|24|5</code>")
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(
        PromoCreationStates.ENTER_SIMPLE if promo_type == "simple" 
        else PromoCreationStates.ENTER_REFERRAL
    )

@admin_router.message(PromoCreationStates.ENTER_SIMPLE)
@inject
async def process_simple_promo(
    message: Message, 
    state: FSMContext,
    session: FromDishka[AsyncSession]
):
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
        ])
        name, reward, limit, hours = message.text.split("|")
        promocode = Promocode(
            name=name.strip(),
            type=PromocodeType.simple,
            reward=float(reward.strip()),
            remaining_usages=int(limit.strip()),
            expires_at=datetime.utcnow() + timedelta(hours=int(hours.strip())),
            required_referrals=0
        )
        session.add(promocode)
        await session.commit()
        
        await message.answer("✅ Простой промокод успешно создан!",reply_markup=keyboard)
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}",reply_markup=keyboard)
        await state.clear()

@admin_router.message(PromoCreationStates.ENTER_REFERRAL)
@inject
async def process_referral_promo(
    message: Message, 
    state: FSMContext,
    session: FromDishka[AsyncSession]
):
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
        ])
        name, reward, limit, hours, req_refs = message.text.split("|")
        promocode = Promocode(
            name=name.strip(),
            type=PromocodeType.referral_based,
            reward=float(reward.strip()),
            remaining_usages=int(limit.strip()),
            expires_at=datetime.utcnow() + timedelta(hours=int(hours.strip())),
            required_referrals=int(req_refs.strip())
        )
        session.add(promocode)
        await session.commit()
        
        await message.answer("✅ Реферальный промокод успешно создан!",reply_markup=keyboard)
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}",reply_markup=keyboard)
        await state.clear()