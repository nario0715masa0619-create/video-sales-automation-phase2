"""
Domain models for VSA Phase2-Core

MasterLead represents a single row in the Master Leads Google Sheet.
All 52 fields are defined with appropriate types and defaults.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from vsa.shared.enums import (
    RecordStatus, LeadStage, CorpType, LeadRank, SalesStatus,
    YouTubeScrapeStatus, OfficialSiteStatus, SourceType,
    CrawlScope, CrawlStatus, PhoneConfidence, EmailConfidence,
    ContactFormStatus, ContactFormRequiredFields,
    EmailValidationStatus, MailSendable, ContactFormSendable,
    OutreachChannel, ContactabilityStatus, OutreachBlockReason,
    LastContactChannel, LastContactResult, DealStatus, PrimarySourceType,
)

@dataclass
class MasterLead:
    """
    Master Leads row model (52 fields).
    
    Represents a single lead candidate being tracked through the sales pipeline.
    All state is maintained here; history is stored in supplementary logs.
    """
    
    # A-L: Identification & Operations (12)
    lead_id: str
    record_status: RecordStatus
    lead_stage: LeadStage
    canonical_company_name: str
    corp_type: Optional[str] = None
    industry: Optional[str] = None
    company_prefecture: Optional[str] = None
    owner: Optional[str] = None
    lead_rank: Optional[LeadRank] = None
    ng_flag: bool = False
    sales_status: Optional[SalesStatus] = None
    memo: Optional[str] = None
    
    # M-T: YouTube Discovery (8)
    youtube_channel_id: Optional[str] = None
    youtube_channel_url: Optional[str] = None
    youtube_channel_name: Optional[str] = None
    youtube_handle: Optional[str] = None
    youtube_description: Optional[str] = None
    youtube_external_links: Optional[str] = None
    youtube_discovered_at: Optional[datetime] = None
    youtube_scrape_status: Optional[YouTubeScrapeStatus] = None
    
    # U-AC: Official Site & Sources (9)
    official_url: Optional[str] = None
    official_domain: Optional[str] = None
    official_site_status: Optional[OfficialSiteStatus] = None
    official_company_name: Optional[str] = None
    official_company_name_source_url: Optional[str] = None
    company_address: Optional[str] = None
    source_type: Optional[SourceType] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    
    # AD-AL: Crawl Control & Execution (9)
    crawl_enabled: bool = False
    crawl_scope: Optional[CrawlScope] = None
    crawl_target_pages: Optional[str] = None
    crawl_priority: Optional[int] = None
    last_crawled_at: Optional[datetime] = None
    crawl_status: Optional[CrawlStatus] = None
    pages_scanned: Optional[int] = None
    crawl_error_code: Optional[str] = None
    crawl_error_message: Optional[str] = None
    
    # AM-AV: Contact Extraction (10)
    phone_number: Optional[str] = None
    phone_source_url: Optional[str] = None
    phone_confidence: Optional[PhoneConfidence] = None
    official_email: Optional[str] = None
    email_source_url: Optional[str] = None
    email_confidence: Optional[EmailConfidence] = None
    contact_form_url: Optional[str] = None
    contact_form_status: Optional[ContactFormStatus] = None
    contact_form_required_fields: Optional[ContactFormRequiredFields] = None
    contact_evidence_summary: Optional[str] = None
    
    # AW-BG: Validation & Outreach (11)
    email_validation_status: Optional[EmailValidationStatus] = None
    email_validation_score: Optional[float] = None
    email_validation_provider: Optional[str] = None
    email_validation_at: Optional[datetime] = None
    email_sendable: Optional[MailSendable] = None
    form_sendable: Optional[ContactFormSendable] = None
    preferred_outreach_channel: Optional[OutreachChannel] = None
    contactability_status: Optional[ContactabilityStatus] = None
    outreach_ready: bool = False
    outreach_block_reason: Optional[OutreachBlockReason] = None
    next_action: Optional[str] = None
    
    # BH-BP: Sales Execution Summary (9)
    last_contacted_at: Optional[datetime] = None
    last_contact_channel: Optional[LastContactChannel] = None
    last_contact_result: Optional[LastContactResult] = None
    email_contact_count: int = 0
    form_contact_count: int = 0
    reply_count: int = 0
    last_reply_at: Optional[datetime] = None
    deal_status: Optional[DealStatus] = None
    next_contact_at: Optional[datetime] = None
    
    # BQ-BU: Audit (5)
    identity_confidence: Optional[str] = None
    primary_source_type: Optional[PrimarySourceType] = None
    primary_source_ref: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def mark_updated(self) -> None:
        """Update the timestamp to current time."""
        self.updated_at = datetime.now()
    
    def is_valid_for_outreach(self) -> bool:
        """
        Check if lead is eligible for outreach.
        
        Rules:
        - record_status must be 'active'
        - ng_flag must be False
        - sales_status must not be (won, lost, ng)
        - contactability_status must not be 'unreachable'
        - outreach_ready must be True (optionally)
        """
        if self.record_status != RecordStatus.ACTIVE:
            return False
        if self.ng_flag:
            return False
        if self.sales_status in (SalesStatus.WON, SalesStatus.LOST, SalesStatus.NG):
            return False
        if self.contactability_status == ContactabilityStatus.UNREACHABLE:
            return False
        return True
