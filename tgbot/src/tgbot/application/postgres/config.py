import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PostgresConfig:
    url: str


def env_var_by_key(key: str) -> str:
    value = os.getenv(key)
    if not value:
        message = f"Env var {key} doesn't exist"
        raise Exception(message)
    return value


def async_postgres_config_from_env() -> PostgresConfig:
    db_name = env_var_by_key("POSTGRES_DB")
    db_password = env_var_by_key("POSTGRES_PASSWORD")
    db_host = env_var_by_key("POSTGRES_HOST")
    db_port = env_var_by_key("POSTGRES_PORT")
    db_user = env_var_by_key("POSTGRES_USER")

    return PostgresConfig(
        f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )


def sync_postgres_config_from_env() -> PostgresConfig:
    db_name = env_var_by_key("POSTGRES_DB")
    db_password = env_var_by_key("POSTGRES_PASSWORD")
    db_host = env_var_by_key("POSTGRES_HOST")
    db_port = env_var_by_key("POSTGRES_PORT")
    db_user = env_var_by_key("POSTGRES_USER")

    return PostgresConfig(
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
