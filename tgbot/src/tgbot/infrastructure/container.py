__all__ = ("ioc_container_factory",)

from dishka import Provider, Scope, AsyncContainer, make_async_container

from tgbot.application.postgres.connection import (
    get_sqlalchemy_async_engine,
    get_sqlalchemy_async_session,
)
from tgbot.application.postgres.config import (
    PostgresConfig,
    async_postgres_config_from_env,
)


def ioc_container_factory() -> AsyncContainer:
    provider = Provider()
    context = {PostgresConfig: async_postgres_config_from_env()}

    provider.from_context(PostgresConfig, scope=Scope.APP)

    provider.provide(
        get_sqlalchemy_async_engine,
        scope=Scope.APP,
    )

    provider.provide(
        get_sqlalchemy_async_session,
        scope=Scope.REQUEST,
    )

    return make_async_container(provider, context=context)
