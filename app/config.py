from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskiqSettings(BaseSettings):
    broker_url: str = "redis://localhost:6379"


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
    taskiq: TaskiqSettings = TaskiqSettings()
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/domomir"
    echo_db: bool = False

    serve_local_images: bool = True
    local_images_url: str = "/images"
    local_images_directory_path: str = "upload/images"
    app_version: str = "local"


@lru_cache
def get_settings():
    return Settings()
