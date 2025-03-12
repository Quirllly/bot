from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)

from tgbot.application.postgres.config import (
    PostgresConfig,
)


def get_sqlalchemy_async_engine(
    async_postgres_config: PostgresConfig,
) -> AsyncEngine:
    return create_async_engine(async_postgres_config.url)


async def get_sqlalchemy_async_session(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async_session_local = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_local() as session:
        yield session
