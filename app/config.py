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
    app_version: str = "local"

    serve_local_images: bool = True

    upload_images_dir: str = "upload/images"

    imagor_url: str = "http://localhost:5555/unsafe"
    local_images_url: str = "/images"


@lru_cache
def get_settings():
    return Settings()
