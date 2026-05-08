"""
Settings loader for VSA Phase2-Core

Loads configuration from .env file and environment variables using Pydantic.
"""

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables"""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Environment
    env: str = Field(default="development", description="Environment (development/staging/production)")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Google Sheets
    google_sheet_id: str = Field(default="", description="Master Leads Google Sheet ID")
    google_service_account_json: str = Field(default="credentials/service_account.json", 
                                            description="Google Service Account JSON file path")
    
    # CRM & Phase 5
    crm_sheet_id: Optional[str] = Field(default=None, description="CRM Google Sheet ID")
    phase5_sheet_id: Optional[str] = Field(default=None, description="Phase 5 Google Sheet ID")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level (DEBUG/INFO/WARNING/ERROR)")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # Crawling
    crawl_timeout_seconds: int = Field(default=30, description="Web crawl timeout")
    crawl_max_pages_per_lead: int = Field(default=5, description="Max pages to crawl per lead")
    crawl_retry_count: int = Field(default=3, description="Retry count for failed crawls")
    
    # Email Validation
    zerobounce_api_key: Optional[str] = Field(default=None, description="ZeroBounce API key")

def load_settings() -> Settings:
    """
    Load settings from .env and environment variables
    
    Returns:
        Settings instance
    """
    return Settings()
