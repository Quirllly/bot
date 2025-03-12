from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.application.postgres.models import Task
from tgbot.application.postgres.models  import UserTaskData
from uuid import UUID
class TaskGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def by_tg_id(self, tg_id: int) -> Task | None:
        task = await self._session.scalar(
            select(Task).where(Task.tg_id == str(tg_id))
        )
        return task

    async def get_task_by_type(self, task_type: str) -> Task | None:
        """
        Ищет задачу по её типу.
        """
        task = await self._session.scalar(
            select(Task).where(Task.type == task_type)
        )
        return task
    
    async def get_all_tasks(self):
        result = await self._session.execute(select(Task))
        return result.scalars().all()
    
    async def get_task_by_id(self, id: int) -> Task | None:
        """
        Ищет задачу по её типу.
        """
        task = await self._session.scalar(
            select(Task).where(Task.id == id)
        )
        return task
    async def get_next_task(self, user_id: UUID) -> Optional[Task]:
        print(f"Получаем следующую задачу для пользователя {user_id}")
        # Получаем все задания, отсортированные по порядку
        all_tasks = await self._session.execute(select(Task).order_by(Task.id))
        all_tasks = all_tasks.scalars().all()
        print(f"Всего задач: {len(all_tasks)}")
        
        # Получаем выполненные задания пользователя
        user_data = await self._session.get(UserTaskData, user_id)
        print(f"Данные пользователя: {user_data}")
        completed_ids = user_data.completed_tasks if user_data else []
        print(f"Выполненные задачи: {completed_ids}")

        # Находим первое невыполненное задание
        for task in all_tasks:
            if task.id not in completed_ids:
                print(f"Найдена невыполненная задача: {task.id}")
                return task
        print("Все задачи выполнены")
        return None
    async def mark_task_completed(self, user_id: UUID, task_id: int) -> None:
        try:
            user_data = await self._session.get(UserTaskData, user_id)
            if not user_data:
                user_data = UserTaskData(user_id=user_id, completed_tasks=[])
                self._session.add(user_data)
            
            if user_data.completed_tasks is None:
                user_data.completed_tasks = []
            
            if task_id not in user_data.completed_tasks:
                user_data.completed_tasks = user_data.completed_tasks + [task_id]

                print(f"Задача {task_id} добавлена в completed_tasks пользователя {user_id}")
                print(f"Текущие выполненные задачи: {user_data.completed_tasks}")
                
                await self._session.commit()
                await self._session.refresh(user_data)  # Обновляем объект
                print(f"Обновленные выполненные задачи: {user_data.completed_tasks}")
            else:
                print(f"Задача {task_id} уже выполнена пользователем {user_id}")
        except Exception as e:
            print(f"Ошибка при сохранении изменений: {e}")
            await self._session.rollback()  # Откатываем транзакцию в случае ошибки