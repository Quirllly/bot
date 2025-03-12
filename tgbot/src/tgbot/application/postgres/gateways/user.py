from uuid import UUID
from datetime import datetime, timedelta
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.application.postgres.models import User, Task, UserTaskData
import logging

logger = logging.getLogger(__name__)

class UserGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def by_tg_id(self, tg_id: int) -> User | None:
        user = await self._session.scalar(
            select(User).where(User.tg_id == str(tg_id))
        )
        return user
    
    async def by_id(self, id: UUID) -> User | None:
        user = await self._session.scalar(
            select(User).where(User.id == id)  # Используем UUID объект напрямую
        )
        return user

    async def by_referral_code(self, referral_code: str) -> User | None:
        user = await self._session.scalar(
            select(User).where(User.referral_code == referral_code)
        )
        return user

    async def top_referrals_all_time(self) -> Sequence[User]:
        users = (
            await self._session.execute(
                select(User)
                .order_by(User.amount_of_referrals.desc())
                .limit(10)
            )
        ).scalars()

        return users
    async def get_user_position(self, tg_id: int) -> int:
        tg_id = str(tg_id)
        user = await self.by_tg_id(tg_id)
        if not user:
            logger.warning(f"Пользователь с tg_id={tg_id} не найден")
            return 0

        last_24_hours = datetime.now() - timedelta(days=1)
        logger.info(f"Запрос позиции пользователя {user.username} за последние 24 часа")

        count_stmt = select(func.count(User.id)).where(
            User.referrer == user.id, User.verify_timestamp >= last_24_hours
        )
        user_referrals_count = (await self._session.execute(count_stmt)).scalar_one()
        logger.info(f"Количество рефералов пользователя: {user_referrals_count}")

        position_stmt = select(func.count(User.id)).where(
            User.verify_timestamp >= last_24_hours,
            User.referrer != None,
            User.referrer != user.id,
        )
        position = (await self._session.execute(position_stmt)).scalar_one()
        logger.info(f"Позиция пользователя: {position + 1}")

        return position + 1
    async def top_referrals_last_day(self, amount: int) -> Sequence[User]:
        last_24_hours = datetime.now() - timedelta(days=1)
        logger.info(f"Запрос топ-{amount} рефералов за последние 24 часа")

        inviter = aliased(User)
        referral = aliased(User)

        result = (
            await self._session.execute(
                select(
                    inviter,
                    func.count(referral.id).label("new_referrals"),
                )
                .select_from(inviter)
                .join(referral, referral.referrer == inviter.id)
                .where(referral.verify_timestamp >= last_24_hours)
                .group_by(inviter.id)
                .order_by(func.count(referral.id).desc())
                .limit(amount)
            )
        ).all()

        logger.info(f"Результат запроса: {result}")
        return result

    async def last_day_referrals_amount(self, tg_id: int) -> int:
        tg_id = str(tg_id)
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return 0

        one_day_ago = datetime.now() - timedelta(days=1)

        count_stmt = select(func.count(User.id)).where(
            User.referrer == user.id, User.verify_timestamp >= one_day_ago
        )
        count_result = await self._session.execute(count_stmt)
        invited_count = count_result.scalar_one()
        return invited_count

    async def tasks_for_user(self, user_id: UUID) -> Sequence[Task] | None:
        stmt = select(Task).where(
            ~Task.id.in_(
                select(UserTaskData.c.task_id).where(
                    user_taskUserTaskData_table.c.user_id == user_id
                )
            )
        )
        result = await self._session.execute(stmt)
        not_completed_tasks = result.scalars().all()

        return not_completed_tasks

    # async def complete_task(self, user_id: UUID) -> Sequence
