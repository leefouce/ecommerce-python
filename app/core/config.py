import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    token_secret: str = "development-secret-change-me"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./ecommerce.db"


def get_settings() -> Settings:
    return Settings(
        token_secret=os.getenv("APP_TOKEN_SECRET", Settings.token_secret),
        access_token_expire_minutes=int(
            os.getenv(
                "APP_ACCESS_TOKEN_EXPIRE_MINUTES",
                str(Settings.access_token_expire_minutes),
            )
        ),
        database_url=os.getenv("APP_DATABASE_URL", Settings.database_url),
    )
