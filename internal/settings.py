from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5435/postgres"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    api_key: str

    max_attempts: int = 3
    retry_base_delay_ms: int = 2000
    webhook_timeout: float = 5.0


settings = Settings()
