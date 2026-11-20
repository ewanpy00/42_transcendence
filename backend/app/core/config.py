from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Language Exchange API"
    debug: bool = False

    secret_key: str = ""
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    frontend_url: str = "https://localhost"
    cors_origins: list[str] = []

    upload_dir: str = "/app/uploads"
    max_upload_mb: int = 10
    rate_limit_per_minute: int = 60

    @property
    def allowed_origins(self) -> list[str]:
        return list({self.frontend_url, *self.cors_origins})


@lru_cache
def get_settings() -> Settings:
    return Settings()
