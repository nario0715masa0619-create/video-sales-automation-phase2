from enum import Enum

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
