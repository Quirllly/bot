from cryptography.fernet import Fernet
from aiogram import Bot
import aiohttp
from tgbot.application.postgres.models import Task, TaskType, UserTaskData  # Добавляем импорт моделей
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import CheckChatInviteRequest
from aiogram.types import ChatJoinRequest
from aiogram.types.chat_join_request import ChatJoinRequest
# Ваши api_id и api_hash
api_id = '21959073'
api_hash = '8c716dde8cdea304fcffec546f532303'

class TaskChecker:
    def __init__(self, bot: Bot , session):  # Добавляем session
        self.bot = bot
        self.session = session  # Сохраняем сессию
        self.client = TelegramClient('session_name', api_id, api_hash)

    async def verify(self, user_id: int, task: Task) -> bool:
        print(f"{task.type}")
        if task.type == TaskType.SUBSCRIPTION:
            print(f"Проверяем подписку пользователя {user_id} на канал {task.channel_id}")
            return await self._check_subscription(user_id, task)
        elif task.type == TaskType.INVITE_LINK:
            print(f"Проверяем ссылку на приглашение пользователя {user_id} на канал {task.chat_id}")
            return await self._check_invite_link(user_id, task)
        elif task.type == TaskType.BOT_START:
            print(f"Проверяем старт бота пользователя {user_id}")
            return await self._check_bot_start(user_id, task)
        return False

    async def _check_subscription(self, user_id: int, task: Task) -> bool:
        try:
            channel_id = f"https://t.me/{task.channel_id[1:]}"
            print(f"Проверяем подписку пользователя {user_id} на канал {channel_id}")
            chat_id = await self.bot.get_chat(task.chat_id)
            print(f"ID канала: {chat_id.id}")
            member = await self.bot.get_chat_member(task.chat_id, user_id)
            print(f"Статус пользователя: {member.status}")
            return member.status in ["member", "administrator", "creator"]
        except Exception as e:
            print(f"Ошибка {e} при проверке подписки пользователя {user_id} на канал {task.channel_id}")
            return False

    async def _check_invite_link(self, user_id: int, task: Task) -> bool:
        try:
            # Пытаемся одобрить заявку на вступление в чат.
            await self.bot.approve_chat_join_request(task.chat_id, user_id)
            print(f"Заявка пользователя {user_id} успешно одобрена.")
            return True
        except Exception as e:
            print(f"Ошибка при проверке заявки на вступление: {e}")
            return False


    async def _check_bot_start(self, user_id: int, task: Task) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.telegram.org/bot{task.bot_token}/getChatMember",
                    params={"chat_id": user_id, "user_id": user_id}
                ) as resp:
                    data = await resp.json()
                    return data.get("result", {}).get("status") in ["member", "administrator", "creator"]
        except Exception as e:
            print(f"Ошибка {e} при проверке статуса пользователя {user_id} в боте {task.bot_token}")
            return False