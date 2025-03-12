from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.application.postgres.models import Subscription


class SubscribeGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_subscribe(self, user_id: UUID, sponsor_id: UUID) -> None:
        new_subscribe = Subscription(user_id=user_id, sponsor_id=sponsor_id)
        self._session.add(new_subscribe)

        await self._session.commit()

    async def by_user_id_and_sponsor_id(
        self, *, user_id: UUID, sponsor_id: UUID
    ) -> Subscription | None:
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.sponsor_id == sponsor_id,
        )
        result = await self._session.execute(stmt)

        return result.scalars().first()
