from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from tgbot.application.postgres.models import Metadata


class MetadataGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def by_name(self, name: str) -> Metadata:
        instruction = await self._session.scalar(
            select(Metadata).where(Metadata.name == name)
        )
        if not instruction:
            raise Exception()

        return instruction
