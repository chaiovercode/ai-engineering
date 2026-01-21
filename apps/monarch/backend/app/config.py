from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Monarch Report Transformer"
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3007"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
