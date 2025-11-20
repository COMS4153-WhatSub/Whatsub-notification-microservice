from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    app_name: str = Field(default="whatsub-notifications")
    port: int = Field(default=8082, alias="PORT")
    log_level: str = Field(default="INFO")
    
    # Database settings
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=3306)
    db_user: str = Field(default="notify_user")
    db_pass: str = Field(default="password")
    db_name: str = Field(default="notification_db")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

