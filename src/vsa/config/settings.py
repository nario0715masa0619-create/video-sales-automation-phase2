from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "development"
    debug: bool = False
    google_sheet_id: str = ""
    google_credentials_file: Optional[str] = None
    google_credentials_json: Optional[str] = None
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    log_format: str = "json"
    crawl_timeout_seconds: int = 30
    crawl_max_pages_per_lead: int = 10
    crawl_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    zerobounce_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def validate_required_fields(self) -> None:
        if not self.google_sheet_id:
            raise ValueError("GOOGLE_SHEET_ID is required")

def load_settings() -> Settings:
    settings = Settings()
    if settings.env == "production":
        settings.validate_required_fields()
    return settings
