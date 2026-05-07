"""
Enum definitions for VSA Phase2-Core

All enum values are lowercase snake_case strings matching Google Sheets conventions.
"""

from enum import Enum

# === Identification & Operations ===

class RecordStatus(str, Enum):
    """Record status (A列)"""
    ACTIVE = "active"
    ARCHIVED = "archived"

class LeadStage(str, Enum):
    """Lead stage progression (C列)"""
    DISCOVERED_FROM_YOUTUBE = "discovered_from_youtube"
    OFFICIAL_URL_IDENTIFIED = "official_url_identified"
    OFFICIAL_SITE_SCRAPED = "official_site_scraped"
    CONTACT_EXTRACTED = "contact_extracted"
    VALIDATED = "validated"
    OUTREACH_READY = "outreach_ready"

class CorpType(str, Enum):
    """Corporation type (E列)"""
    CORPORATION = "corporation"
    LLC = "llc"
    SOLE_PROPRIETOR = "sole_proprietor"
    PARTNERSHIP = "partnership"
    UNKNOWN = "unknown"

class LeadRank(str, Enum):
    """Lead priority rank (I列)"""
    S = "s"
    A = "a"
    B = "b"
    C = "c"

class SalesStatus(str, Enum):
    """Sales outcome status (K列)"""
    WON = "won"
    LOST = "lost"
    NG = "ng"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"

# === YouTube Discovery ===

class YouTubeScrapeStatus(str, Enum):
    """YouTube scrape status (T列)"""
    NOT_SCRAPED = "not_scraped"
    SCRAPED = "scraped"
    FAILED = "failed"

# === Official Site & Sources ===

class OfficialSiteStatus(str, Enum):
    """Official site verification status (U列)"""
    NOT_CHECKED = "not_checked"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    NO_OFFICIAL_SITE = "no_official_site"

class SourceType(str, Enum):
    """Data source type (W列)"""
    YOUTUBE = "youtube"
    OFFICIAL_SITE = "official_site"
    MANUAL = "manual"
    CRM = "crm"
    OTHER = "other"

# === Crawl Control & Execution ===

class CrawlScope(str, Enum):
    """Crawl scope for official site (AE列)"""
    FOCUSED = "focused"
    STANDARD = "standard"
    DEEP = "deep"
    DISABLED = "disabled"

class CrawlStatus(str, Enum):
    """Crawl execution status (AJ列)"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

# === Contact Extraction ===

class PhoneConfidence(str, Enum):
    """Phone number confidence (AO列)"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class EmailConfidence(str, Enum):
    """Email confidence (AR列)"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ContactFormStatus(str, Enum):
    """Contact form presence status (AT列)"""
    NO_FORM = "no_form"
    NOT_CHECKED = "not_checked"
    FOUND = "found"
    NOT_FOUND = "not_found"

class ContactFormRequiredFields(str, Enum):
    """Contact form required fields (AU列)"""
    NONE = "none"
    EMAIL = "email"
    NAME = "name"
    COMPANY = "company"
    MESSAGE = "message"
    PHONE = "phone"
    MULTIPLE = "multiple"

# === Validation & Outreach ===

class EmailValidationStatus(str, Enum):
    """Email validation status from provider (AW列)"""
    NOT_VALIDATED = "not_validated"
    VALID = "valid"
    INVALID = "invalid"
    RISKY = "risky"
    UNKNOWN = "unknown"

class MailSendable(str, Enum):
    """Email sendability (AZ列)"""
    TRUE = "TRUE"
    FALSE = "FALSE"

class ContactFormSendable(str, Enum):
    """Form submission feasibility (BA列)"""
    TRUE = "TRUE"
    FALSE = "FALSE"

class OutreachChannel(str, Enum):
    """Preferred outreach channel (BB列)"""
    EMAIL = "email"
    FORM = "form"
    NONE = "none"

class ContactabilityStatus(str, Enum):
    """Overall contactability judgment (BC列)"""
    REACHABLE = "reachable"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"

class OutreachBlockReason(str, Enum):
    """Reason for blocking outreach (BE列)"""
    NG_FLAG = "ng_flag"
    NO_VALID_CONTACT = "no_valid_contact"
    NOT_OUTREACH_READY = "not_outreach_ready"
    SALES_STATUS_BLOCKED = "sales_status_blocked"
    NONE = "none"

# === Sales Execution Summary ===

class LastContactChannel(str, Enum):
    """Last contact channel (BH列)"""
    EMAIL = "email"
    FORM = "form"
    PHONE = "phone"
    OTHER = "other"

class LastContactResult(str, Enum):
    """Last contact result (BI列)"""
    NO_RESPONSE = "no_response"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    INTERESTED_BUT_TIMING = "interested_but_timing"
    CALL_BACK_LATER = "call_back_later"
    INVALID_CONTACT = "invalid_contact"

class DealStatus(str, Enum):
    """Deal outcome (BO列)"""
    WON = "won"
    LOST = "lost"
    NG = "ng"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"

# === Audit ===

class PrimarySourceType(str, Enum):
    """Primary source of lead (BR列)"""
    YOUTUBE = "youtube"
    OFFICIAL_SITE = "official_site"
    MANUAL = "manual"
    CRM = "crm"
    OTHER = "other"
