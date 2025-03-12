from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.application.postgres.models import UserTaskData


class UserTaskGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, task_id: int, user_id: int) -> None:
        stmt = insert(UserTaskData).values(user_id=user_id, task_id=task_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def by_user_task(self, task_id: int, user_id: int) -> dict | None:
        stmt = select(UserTaskData).where(
            UserTaskData.c.user_id == user_id,
            UserTaskData.c.task_id == task_id,
        )
        result = await self._session.execute(stmt)
        row = result.fetchone()

        if row:
            return dict(row._mapping) 
        return None
