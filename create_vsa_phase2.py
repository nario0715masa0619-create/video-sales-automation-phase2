#!/usr/bin/env python3
import os
from pathlib import Path

def create_file(file_path: str, content: str):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ {file_path}")

def main():
    print("🚀 VSA Phase2-Core Foundation 自動生成\n")
    
    # ディレクトリ作成
    dirs = ["src/vsa/config", "src/vsa/domain", "src/vsa/application", 
            "src/vsa/infrastructure", "src/vsa/interfaces", "src/vsa/shared", "tests"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✓ ディレクトリ作成完了\n")
    
    # pyproject.toml
    create_file("pyproject.toml", """[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[project]
name = "video-sales-automation-phase2"
version = "0.1.0"
description = "Phase2 Core: Clean slate for video sales automation"
readme = "README.md"
requires-python = ">=3.9"
authors = [{name = "Video Sales Team"}]
license = {text = "MIT"}

dependencies = [
    "python-dotenv>=1.0.0",
    "google-auth-oauthlib>=1.0.0",
    "google-api-python-client>=2.90.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "structlog>=24.0.0",
    "click>=8.1.0",
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.7.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[project.scripts]
vsa = "vsa.interfaces.cli:main"

[tool.black]
line-length = 100
target-version = ['py39']

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --tb=short"
""")
    
    create_file(".env.example", """ENV=development
DEBUG=false
GOOGLE_SHEET_ID=your_spreadsheet_id_here
LOG_LEVEL=INFO
LOG_FORMAT=json
CRAWL_TIMEOUT_SECONDS=30
CRAWL_MAX_PAGES_PER_LEAD=10
""")
    
    create_file("src/vsa/__init__.py", """\"\"\"Video Sales Automation Phase2 - Core\"\"\"
__version__ = "0.1.0"
__package_name__ = "vsa"
""")
    
    create_file("src/vsa/config/__init__.py", """from vsa.config.settings import Settings
__all__ = ["Settings"]
""")
    
    create_file("src/vsa/config/settings.py", """from pathlib import Path
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
""")
    
    create_file("src/vsa/shared/__init__.py", """from vsa.shared.constants import MasterLeadsColumns
from vsa.shared.enums import RecordStatus, LeadStage, SourceType, CrawlScope, CrawlStatus
__all__ = ["MasterLeadsColumns", "RecordStatus", "LeadStage", "SourceType", "CrawlScope", "CrawlStatus"]
""")
    
    create_file("src/vsa/shared/constants.py", """class MasterLeadsColumns:
    lead_id = "lead_id"
    record_status = "record_status"
    lead_stage = "lead_stage"
    canonical_company_name = "canonical_company_name"
    official_url = "official_url"
    official_domain = "official_domain"
    official_email = "official_email"
    
    @classmethod
    def all_columns(cls):
        return [cls.lead_id, cls.record_status, cls.lead_stage, cls.canonical_company_name,
                cls.official_url, cls.official_domain, cls.official_email]
""")
    
    create_file("src/vsa/shared/enums.py", """from enum import Enum

class RecordStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class LeadStage(str, Enum):
    DISCOVERED_FROM_YOUTUBE = "discovered_from_youtube"
    VALIDATED = "validated"
    OUTREACH_READY = "outreach_ready"

class SourceType(str, Enum):
    YOUTUBE = "youtube"
    OFFICIAL_SITE = "official_site"

class CrawlScope(str, Enum):
    FOCUSED = "focused"
    DISABLED = "disabled"

class CrawlStatus(str, Enum):
    NOT_STARTED = "not_started"
    SUCCESS = "success"
""")
    
    create_file("src/vsa/domain/__init__.py", """from vsa.domain.models import MasterLead
__all__ = ["MasterLead"]
""")
    
    create_file("src/vsa/domain/models.py", """from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from vsa.shared.enums import RecordStatus, LeadStage

@dataclass
class MasterLead:
    lead_id: str
    record_status: RecordStatus
    lead_stage: LeadStage
    canonical_company_name: str
    ng_flag: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def mark_updated(self) -> None:
        self.updated_at = datetime.now()
    
    def is_valid_for_outreach(self) -> bool:
        return self.record_status == RecordStatus.ACTIVE and not self.ng_flag
""")
    
    create_file("src/vsa/application/__init__.py", "\"\"\"Application layer\"\"\"")
    create_file("src/vsa/infrastructure/__init__.py", "\"\"\"Infrastructure layer\"\"\"")
    
    create_file("src/vsa/infrastructure/repository.py", """from abc import ABC, abstractmethod
from typing import List, Optional
from vsa.domain.models import MasterLead

class MasterLeadsRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[MasterLead]:
        pass
    
    @abstractmethod
    def get_by_id(self, lead_id: str) -> Optional[MasterLead]:
        pass
    
    @abstractmethod
    def save(self, lead: MasterLead) -> None:
        pass

class GoogleSheetsRepository(MasterLeadsRepository):
    def __init__(self, sheet_id: str, credentials_file: Optional[str] = None):
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
    
    def get_all(self) -> List[MasterLead]:
        raise NotImplementedError()
    
    def get_by_id(self, lead_id: str) -> Optional[MasterLead]:
        raise NotImplementedError()
    
    def save(self, lead: MasterLead) -> None:
        raise NotImplementedError()
""")
    
    create_file("src/vsa/interfaces/__init__.py", "\"\"\"Interface layer\"\"\"")
    
    create_file("src/vsa/interfaces/logging_setup.py", """import structlog
from vsa.config.settings import Settings

def setup_logging(settings: Settings):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    return structlog.get_logger()
""")
    
    create_file("src/vsa/interfaces/cli.py", """import click
from vsa.config.settings import load_settings
from vsa.interfaces.logging_setup import setup_logging

@click.group()
@click.option("--env", type=click.Choice(["development", "staging", "production"]), default="development")
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), default="INFO")
@click.pass_context
def cli(ctx, env, log_level):
    settings = load_settings()
    settings.env = env
    settings.log_level = log_level
    logger = setup_logging(settings)
    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings
    ctx.obj["logger"] = logger

@cli.command()
@click.option("--source", type=click.Choice(["phase1"]), required=True)
@click.option("--mode", type=click.Choice(["dry-run", "validate", "execute"]), default="dry-run")
@click.pass_context
def migrate(ctx, source, mode):
    logger = ctx.obj["logger"]
    logger.info("migrate command", source=source, mode=mode)
    click.echo(f"Migration from {source} in {mode} mode")

@cli.command()
@click.option("--action", type=click.Choice(["fetch", "plan", "crawl"]), required=True)
@click.option("--lead-id", type=str, default=None)
@click.pass_context
def sync(ctx, action, lead_id):
    logger = ctx.obj["logger"]
    logger.info("sync command", action=action, lead_id=lead_id)
    click.echo(f"Sync action: {action}")

@cli.command()
@click.pass_context
def version(ctx):
    from vsa import __version__
    click.echo(f"VSA Phase2-Core version {__version__}")

def main():
    cli()

if __name__ == "__main__":
    main()
""")
    
    create_file("tests/__init__.py", "\"\"\"Tests for VSA Phase2-Core\"\"\"")
    
    create_file("tests/test_enums.py", """from vsa.shared.enums import RecordStatus, LeadStage

def test_record_status():
    assert RecordStatus.ACTIVE.value == "active"
    assert RecordStatus.ARCHIVED.value == "archived"

def test_lead_stage():
    assert LeadStage.DISCOVERED_FROM_YOUTUBE.value == "discovered_from_youtube"
""")
    
    create_file("tests/test_models.py", """from vsa.domain.models import MasterLead
from vsa.shared.enums import RecordStatus, LeadStage

def test_create_lead():
    lead = MasterLead(
        lead_id="LEAD001",
        record_status=RecordStatus.ACTIVE,
        lead_stage=LeadStage.DISCOVERED_FROM_YOUTUBE,
        canonical_company_name="Example Corp"
    )
    assert lead.lead_id == "LEAD001"
    assert lead.is_valid_for_outreach() is True

def test_ng_flag():
    lead = MasterLead(
        lead_id="LEAD002",
        record_status=RecordStatus.ACTIVE,
        lead_stage=LeadStage.VALIDATED,
        canonical_company_name="Example Corp",
        ng_flag=True
    )
    assert lead.is_valid_for_outreach() is False
""")
    
    create_file("tests/test_constants.py", """from vsa.shared.constants import MasterLeadsColumns

def test_all_columns():
    columns = MasterLeadsColumns.all_columns()
    assert isinstance(columns, list)
    assert len(columns) > 0

def test_no_duplicates():
    columns = MasterLeadsColumns.all_columns()
    assert len(columns) == len(set(columns))
""")
    
    create_file("tests/test_settings.py", """from vsa.config.settings import Settings

def test_settings_defaults():
    settings = Settings(env="development")
    assert settings.env == "development"
    assert settings.debug is False
""")
    
    print("\n" + "="*50)
    print("✅ すべてのファイルが作成されました！")
    print("="*50)
    print("\n次のステップ:")
    print("  pip install -e '.[dev]'")
    print("  pytest tests/ -v")
    print("  vsa --help")

if __name__ == "__main__":
    main()
