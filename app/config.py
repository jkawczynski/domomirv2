from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
    broker_url: str = "redis://redis:6379"
    result_backend_url: str = "redis://redis:6379"
    enable_utc: bool = True
    timezone: str = "Europe/Warsaw"


class MqttSettings(BaseSettings):
    enabled: bool = False
    host: str | None = None
    user: str | None = None
    password: str | None = None
    port: int = 1883
    topic_prefix: str = "test"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    mqtt: MqttSettings = MqttSettings()
    celery: CelerySettings = CelerySettings()
    database_url: str = "sqlite:///db.sqlite"


@lru_cache
def get_settings():
    return Settings()
