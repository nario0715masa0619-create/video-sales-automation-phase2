"""
Row <-> Model converters for Master Leads

Converts between Google Sheets rows (dicts) and MasterLead domain models.
"""

from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar
import structlog

from vsa.shared.constants import MasterLeadsColumns
from vsa.shared.enums import (
    RecordStatus, LeadStage, CorpType, LeadRank, SalesStatus,
    YouTubeScrapeStatus, OfficialSiteStatus, SourceType,
    CrawlScope, CrawlStatus, PhoneConfidence, EmailConfidence,
    ContactFormStatus, ContactFormRequiredFields,
    EmailValidationStatus, MailSendable, ContactFormSendable,
    OutreachChannel, ContactabilityStatus, OutreachBlockReason,
    LastContactChannel, LastContactResult, DealStatus, PrimarySourceType,
)
from vsa.domain.models import MasterLead

logger = structlog.get_logger(__name__)

T = TypeVar('T')

class RowToModelConverter:
    """Converts between Google Sheets rows and MasterLead models."""
    
    @staticmethod
    def sheet_row_to_model(row: Dict[str, Any]) -> MasterLead:
        """
        Convert a Google Sheets row (dict) to a MasterLead model.
        
        Args:
            row: Dict mapping column names to values
            
        Returns:
            MasterLead instance
        """
        def get_str(col_name: str) -> Optional[str]:
            val = row.get(col_name, "")
            return val if val and val.strip() else None
        
        def get_bool(col_name: str) -> bool:
            val = row.get(col_name, "").upper()
            return val == "TRUE"
        
        def get_int(col_name: str) -> Optional[int]:
            val = row.get(col_name, "")
            try:
                return int(val) if val else None
            except (ValueError, TypeError):
                return None
        
        def get_float(col_name: str) -> Optional[float]:
            val = row.get(col_name, "")
            try:
                return float(val) if val else None
            except (ValueError, TypeError):
                return None
        
        def get_datetime(col_name: str) -> Optional[datetime]:
            val = get_str(col_name)
            if not val:
                return None
            try:
                return datetime.fromisoformat(val)
            except (ValueError, TypeError):
                logger.warning("Failed to parse datetime", col=col_name, val=val)
                return None
        
        def get_enum(enum_type: Type[T], col_name: str, default: Optional[T] = None) -> Optional[T]:
            val = get_str(col_name)
            if not val:
                return default
            try:
                return enum_type(val)
            except (ValueError, KeyError):
                logger.warning("Failed to parse enum", enum_type=enum_type.__name__, col=col_name, val=val)
                return default
        
        return MasterLead(
            # A-L: Identification & Operations
            lead_id=get_str(MasterLeadsColumns.lead_id) or "UNKNOWN",
            record_status=get_enum(RecordStatus, MasterLeadsColumns.record_status, RecordStatus.ACTIVE),
            lead_stage=get_enum(LeadStage, MasterLeadsColumns.lead_stage, LeadStage.DISCOVERED_FROM_YOUTUBE),
            canonical_company_name=get_str(MasterLeadsColumns.canonical_company_name) or "",
            corp_type=get_str(MasterLeadsColumns.corp_type),
            industry=get_str(MasterLeadsColumns.industry),
            company_prefecture=get_str(MasterLeadsColumns.company_prefecture),
            owner=get_str(MasterLeadsColumns.owner),
            lead_rank=get_enum(LeadRank, MasterLeadsColumns.lead_rank),
            ng_flag=get_bool(MasterLeadsColumns.ng_flag),
            sales_status=get_enum(SalesStatus, MasterLeadsColumns.sales_status),
            memo=get_str(MasterLeadsColumns.memo),
            
            # M-T: YouTube Discovery
            youtube_channel_id=get_str(MasterLeadsColumns.youtube_channel_id),
            youtube_channel_url=get_str(MasterLeadsColumns.youtube_channel_url),
            youtube_channel_name=get_str(MasterLeadsColumns.youtube_channel_name),
            youtube_handle=get_str(MasterLeadsColumns.youtube_handle),
            youtube_description=get_str(MasterLeadsColumns.youtube_description),
            youtube_external_links=get_str(MasterLeadsColumns.youtube_external_links),
            youtube_discovered_at=get_datetime(MasterLeadsColumns.youtube_discovered_at),
            youtube_scrape_status=get_enum(YouTubeScrapeStatus, MasterLeadsColumns.youtube_scrape_status),
            
            # U-AC: Official Site & Sources
            official_url=get_str(MasterLeadsColumns.official_url),
            official_domain=get_str(MasterLeadsColumns.official_domain),
            official_site_status=get_enum(OfficialSiteStatus, MasterLeadsColumns.official_site_status),
            official_company_name=get_str(MasterLeadsColumns.official_company_name),
            official_company_name_source_url=get_str(MasterLeadsColumns.official_company_name_source_url),
            company_address=get_str(MasterLeadsColumns.company_address),
            source_type=get_enum(SourceType, MasterLeadsColumns.source_type),
            source_name=get_str(MasterLeadsColumns.source_name),
            source_url=get_str(MasterLeadsColumns.source_url),
            
            # AD-AL: Crawl Control & Execution
            crawl_enabled=get_bool(MasterLeadsColumns.crawl_enabled),
            crawl_scope=get_enum(CrawlScope, MasterLeadsColumns.crawl_scope),
            crawl_target_pages=get_str(MasterLeadsColumns.crawl_target_pages),
            crawl_priority=get_int(MasterLeadsColumns.crawl_priority),
            last_crawled_at=get_datetime(MasterLeadsColumns.last_crawled_at),
            crawl_status=get_enum(CrawlStatus, MasterLeadsColumns.crawl_status),
            pages_scanned=get_int(MasterLeadsColumns.pages_scanned),
            crawl_error_code=get_str(MasterLeadsColumns.crawl_error_code),
            crawl_error_message=get_str(MasterLeadsColumns.crawl_error_message),
            
            # AM-AV: Contact Extraction
            phone_number=get_str(MasterLeadsColumns.phone_number),
            phone_source_url=get_str(MasterLeadsColumns.phone_source_url),
            phone_confidence=get_enum(PhoneConfidence, MasterLeadsColumns.phone_confidence),
            official_email=get_str(MasterLeadsColumns.official_email),
            email_source_url=get_str(MasterLeadsColumns.email_source_url),
            email_confidence=get_enum(EmailConfidence, MasterLeadsColumns.email_confidence),
            contact_form_url=get_str(MasterLeadsColumns.contact_form_url),
            contact_form_status=get_enum(ContactFormStatus, MasterLeadsColumns.contact_form_status),
            contact_form_required_fields=get_enum(ContactFormRequiredFields, MasterLeadsColumns.contact_form_required_fields),
            contact_evidence_summary=get_str(MasterLeadsColumns.contact_evidence_summary),
            
            # AW-BG: Validation & Outreach
            email_validation_status=get_enum(EmailValidationStatus, MasterLeadsColumns.email_validation_status),
            email_validation_score=get_float(MasterLeadsColumns.email_validation_score),
            email_validation_provider=get_str(MasterLeadsColumns.email_validation_provider),
            email_validation_at=get_datetime(MasterLeadsColumns.email_validation_at),
            email_sendable=get_enum(MailSendable, MasterLeadsColumns.email_sendable),
            form_sendable=get_enum(ContactFormSendable, MasterLeadsColumns.form_sendable),
            preferred_outreach_channel=get_enum(OutreachChannel, MasterLeadsColumns.preferred_outreach_channel),
            contactability_status=get_enum(ContactabilityStatus, MasterLeadsColumns.contactability_status),
            outreach_ready=get_bool(MasterLeadsColumns.outreach_ready),
            outreach_block_reason=get_enum(OutreachBlockReason, MasterLeadsColumns.outreach_block_reason, OutreachBlockReason.NONE),
            next_action=get_str(MasterLeadsColumns.next_action),
            
            # BH-BP: Sales Execution Summary
            last_contacted_at=get_datetime(MasterLeadsColumns.last_contacted_at),
            last_contact_channel=get_enum(LastContactChannel, MasterLeadsColumns.last_contact_channel),
            last_contact_result=get_enum(LastContactResult, MasterLeadsColumns.last_contact_result),
            email_contact_count=get_int(MasterLeadsColumns.email_contact_count) or 0,
            form_contact_count=get_int(MasterLeadsColumns.form_contact_count) or 0,
            reply_count=get_int(MasterLeadsColumns.reply_count) or 0,
            last_reply_at=get_datetime(MasterLeadsColumns.last_reply_at),
            deal_status=get_enum(DealStatus, MasterLeadsColumns.deal_status),
            next_contact_at=get_datetime(MasterLeadsColumns.next_contact_at),
            
            # BQ-BU: Audit
            identity_confidence=get_str(MasterLeadsColumns.identity_confidence),
            primary_source_type=get_enum(PrimarySourceType, MasterLeadsColumns.primary_source_type),
            primary_source_ref=get_str(MasterLeadsColumns.primary_source_ref),
            created_at=get_datetime(MasterLeadsColumns.created_at) or datetime.now(),
            updated_at=get_datetime(MasterLeadsColumns.updated_at) or datetime.now(),
        )
    
    @staticmethod
    def model_to_sheet_row(lead: MasterLead) -> Dict[str, Any]:
        """
        Convert a MasterLead model to a Google Sheets row (dict).
        
        Args:
            lead: MasterLead instance
            
        Returns:
            Dict mapping column names to values
        """
        def fmt_bool(val: Optional[bool]) -> str:
            return "TRUE" if val else "FALSE"
        
        def fmt_datetime(val: Optional[datetime]) -> str:
            return val.isoformat() if val else ""
        
        def fmt_enum(val: Optional[object]) -> str:
            return val.value if val else ""
        
        def fmt_str(val: Optional[str]) -> str:
            return val or ""
        
        def fmt_int(val: Optional[int]) -> str:
            return str(val) if val is not None else ""
        
        def fmt_float(val: Optional[float]) -> str:
            return str(val) if val is not None else ""
        
        return {
            # A-L
            MasterLeadsColumns.lead_id: lead.lead_id,
            MasterLeadsColumns.record_status: fmt_enum(lead.record_status),
            MasterLeadsColumns.lead_stage: fmt_enum(lead.lead_stage),
            MasterLeadsColumns.canonical_company_name: fmt_str(lead.canonical_company_name),
            MasterLeadsColumns.corp_type: fmt_str(lead.corp_type),
            MasterLeadsColumns.industry: fmt_str(lead.industry),
            MasterLeadsColumns.company_prefecture: fmt_str(lead.company_prefecture),
            MasterLeadsColumns.owner: fmt_str(lead.owner),
            MasterLeadsColumns.lead_rank: fmt_enum(lead.lead_rank),
            MasterLeadsColumns.ng_flag: fmt_bool(lead.ng_flag),
            MasterLeadsColumns.sales_status: fmt_enum(lead.sales_status),
            MasterLeadsColumns.memo: fmt_str(lead.memo),
            
            # M-T
            MasterLeadsColumns.youtube_channel_id: fmt_str(lead.youtube_channel_id),
            MasterLeadsColumns.youtube_channel_url: fmt_str(lead.youtube_channel_url),
            MasterLeadsColumns.youtube_channel_name: fmt_str(lead.youtube_channel_name),
            MasterLeadsColumns.youtube_handle: fmt_str(lead.youtube_handle),
            MasterLeadsColumns.youtube_description: fmt_str(lead.youtube_description),
            MasterLeadsColumns.youtube_external_links: fmt_str(lead.youtube_external_links),
            MasterLeadsColumns.youtube_discovered_at: fmt_datetime(lead.youtube_discovered_at),
            MasterLeadsColumns.youtube_scrape_status: fmt_enum(lead.youtube_scrape_status),
            
            # U-AC
            MasterLeadsColumns.official_url: fmt_str(lead.official_url),
            MasterLeadsColumns.official_domain: fmt_str(lead.official_domain),
            MasterLeadsColumns.official_site_status: fmt_enum(lead.official_site_status),
            MasterLeadsColumns.official_company_name: fmt_str(lead.official_company_name),
            MasterLeadsColumns.official_company_name_source_url: fmt_str(lead.official_company_name_source_url),
            MasterLeadsColumns.company_address: fmt_str(lead.company_address),
            MasterLeadsColumns.source_type: fmt_enum(lead.source_type),
            MasterLeadsColumns.source_name: fmt_str(lead.source_name),
            MasterLeadsColumns.source_url: fmt_str(lead.source_url),
            
            # AD-AL
            MasterLeadsColumns.crawl_enabled: fmt_bool(lead.crawl_enabled),
            MasterLeadsColumns.crawl_scope: fmt_enum(lead.crawl_scope),
            MasterLeadsColumns.crawl_target_pages: fmt_str(lead.crawl_target_pages),
            MasterLeadsColumns.crawl_priority: fmt_int(lead.crawl_priority),
            MasterLeadsColumns.last_crawled_at: fmt_datetime(lead.last_crawled_at),
            MasterLeadsColumns.crawl_status: fmt_enum(lead.crawl_status),
            MasterLeadsColumns.pages_scanned: fmt_int(lead.pages_scanned),
            MasterLeadsColumns.crawl_error_code: fmt_str(lead.crawl_error_code),
            MasterLeadsColumns.crawl_error_message: fmt_str(lead.crawl_error_message),
            
            # AM-AV
            MasterLeadsColumns.phone_number: fmt_str(lead.phone_number),
            MasterLeadsColumns.phone_source_url: fmt_str(lead.phone_source_url),
            MasterLeadsColumns.phone_confidence: fmt_enum(lead.phone_confidence),
            MasterLeadsColumns.official_email: fmt_str(lead.official_email),
            MasterLeadsColumns.email_source_url: fmt_str(lead.email_source_url),
            MasterLeadsColumns.email_confidence: fmt_enum(lead.email_confidence),
            MasterLeadsColumns.contact_form_url: fmt_str(lead.contact_form_url),
            MasterLeadsColumns.contact_form_status: fmt_enum(lead.contact_form_status),
            MasterLeadsColumns.contact_form_required_fields: fmt_enum(lead.contact_form_required_fields),
            MasterLeadsColumns.contact_evidence_summary: fmt_str(lead.contact_evidence_summary),
            
            # AW-BG
            MasterLeadsColumns.email_validation_status: fmt_enum(lead.email_validation_status),
            MasterLeadsColumns.email_validation_score: fmt_float(lead.email_validation_score),
            MasterLeadsColumns.email_validation_provider: fmt_str(lead.email_validation_provider),
            MasterLeadsColumns.email_validation_at: fmt_datetime(lead.email_validation_at),
            MasterLeadsColumns.email_sendable: fmt_enum(lead.email_sendable),
            MasterLeadsColumns.form_sendable: fmt_enum(lead.form_sendable),
            MasterLeadsColumns.preferred_outreach_channel: fmt_enum(lead.preferred_outreach_channel),
            MasterLeadsColumns.contactability_status: fmt_enum(lead.contactability_status),
            MasterLeadsColumns.outreach_ready: fmt_bool(lead.outreach_ready),
            MasterLeadsColumns.outreach_block_reason: fmt_enum(lead.outreach_block_reason),
            MasterLeadsColumns.next_action: fmt_str(lead.next_action),
            
            # BH-BP
            MasterLeadsColumns.last_contacted_at: fmt_datetime(lead.last_contacted_at),
            MasterLeadsColumns.last_contact_channel: fmt_enum(lead.last_contact_channel),
            MasterLeadsColumns.last_contact_result: fmt_enum(lead.last_contact_result),
            MasterLeadsColumns.email_contact_count: fmt_int(lead.email_contact_count),
            MasterLeadsColumns.form_contact_count: fmt_int(lead.form_contact_count),
            MasterLeadsColumns.reply_count: fmt_int(lead.reply_count),
            MasterLeadsColumns.last_reply_at: fmt_datetime(lead.last_reply_at),
            MasterLeadsColumns.deal_status: fmt_enum(lead.deal_status),
            MasterLeadsColumns.next_contact_at: fmt_datetime(lead.next_contact_at),
            
            # BQ-BU
            MasterLeadsColumns.identity_confidence: fmt_str(lead.identity_confidence),
            MasterLeadsColumns.primary_source_type: fmt_enum(lead.primary_source_type),
            MasterLeadsColumns.primary_source_ref: fmt_str(lead.primary_source_ref),
            MasterLeadsColumns.created_at: fmt_datetime(lead.created_at),
            MasterLeadsColumns.updated_at: fmt_datetime(lead.updated_at),
        }
