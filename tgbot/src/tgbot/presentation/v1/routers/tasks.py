from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.application import UserGateway, TaskGateway, UserTaskGateway
from tgbot.presentation.v1.shit import (
    check_with_answer,
)
from tgbot.presentation.v1.shit import (
    check_subscription,
    check_with_answer_for_callbacks,
)
from tgbot.presentation.v1.keyboards import (
    get_subscribe_task_keyboard,
    get_main_keyboard,
    TaskCallback,
)


tasks_router = Router()


@tasks_router.message(F.data == "Задания 📚")
@inject
async def tasks(message: Message, session: FromDishka[AsyncSession], bot: Bot):
    if not await check_with_answer(bot=bot, message=message, session=session):
        return

    user_gateway = UserGateway(session)
    user = await user_gateway.by_tg_id(message.from_user.id)
    tasks = await user_gateway.tasks_for_user(user.id)
    if tasks:
        await message.answer(
            f"Подпишись на канал споносора и получи награду - {tasks[0].reward}",
            reply_markup=get_subscribe_task_keyboard(tasks[0]),
        )
    else:
        await message.answer(
            "Актуальных заданий нет", reply_markup=get_main_keyboard()
        )


@tasks_router.callback_query(TaskCallback.filter())
@inject
async def my_callback_foo(
    callback: CallbackQuery,
    bot: Bot,
    session: FromDishka[AsyncSession],
    callback_data: TaskCallback,
):
    if not await check_with_answer_for_callbacks(
        bot=bot,
        message=callback.message,
        session=session,
        user_tg_id=callback.from_user.id,
    ):
        return

    if await check_subscription(
        user_tg_id=callback.from_user.id,
        channel_id=callback_data.tg_id,
        bot=bot,
    ):
        user_gateway = UserGateway(session)
        task_gateway = TaskGateway(session)
        user_task_gateway = UserTaskGateway(session)

        user = await user_gateway.by_tg_id(callback.from_user.id)
        task = await task_gateway.by_tg_id(callback_data.tg_id)
        user_task = await user_task_gateway.by_user_task(task.id, user.id)
        if user_task:
            await callback.answer(
                "Вы уже получали награду за это задание", show_alert=True
            )
        else:
            user.balance += task.reward
            user.earned += task.reward
            await user_task_gateway.add(task_id=task.id, user_id=user.id)
            await session.commit()
            await callback.answer(
                f"Вы подписались на канал спонсора, вам начислена награда в размере {task.reward}✨",
                show_alert=True,
            )

        task = await user_gateway.tasks_for_user(user.id)
        if task:
            await bot.send_message(
                chat_id=user.tg_id,
                reply_markup=get_subscribe_task_keyboard(task[0]),
                text=f"Подпишись на канал споносора и получи награду - {task[0].reward}",
            )
        else:
            await callback.answer(
                "Актуальных заданий нет", reply_markup=get_main_keyboard()
            )

    else:
        await callback.answer(
            "Вы не подписались на канал спонсора", show_alert=True
        )
