from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from tgbot.application.postgres.models import Sponsor


class SponsorGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def all_sponsors(self) -> Sequence[Sponsor]:
        sponsors = (await self._session.scalars(select(Sponsor))).all()
        return sponsors
