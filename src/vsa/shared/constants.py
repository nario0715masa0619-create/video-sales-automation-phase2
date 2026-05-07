"""
Column name constants for Master Leads sheet

All column names match the Google Sheets data-model.md specification exactly.
"""

class MasterLeadsColumns:
    # A-L: Identification & Operations (12)
    lead_id = "lead_id"
    record_status = "record_status"
    lead_stage = "lead_stage"
    canonical_company_name = "canonical_company_name"
    corp_type = "corp_type"
    industry = "industry"
    company_prefecture = "company_prefecture"
    owner = "owner"
    lead_rank = "lead_rank"
    ng_flag = "ng_flag"
    sales_status = "sales_status"
    memo = "memo"
    
    # M-T: YouTube Discovery (8)
    youtube_channel_id = "youtube_channel_id"
    youtube_channel_url = "youtube_channel_url"
    youtube_channel_name = "youtube_channel_name"
    youtube_handle = "youtube_handle"
    youtube_description = "youtube_description"
    youtube_external_links = "youtube_external_links"
    youtube_discovered_at = "youtube_discovered_at"
    youtube_scrape_status = "youtube_scrape_status"
    
    # U-AC: Official Site & Sources (9)
    official_url = "official_url"
    official_domain = "official_domain"
    official_site_status = "official_site_status"
    official_company_name = "official_company_name"
    official_company_name_source_url = "official_company_name_source_url"
    company_address = "company_address"
    source_type = "source_type"
    source_name = "source_name"
    source_url = "source_url"
    
    # AD-AL: Crawl Control & Execution (9)
    crawl_enabled = "crawl_enabled"
    crawl_scope = "crawl_scope"
    crawl_target_pages = "crawl_target_pages"
    crawl_priority = "crawl_priority"
    last_crawled_at = "last_crawled_at"
    crawl_status = "crawl_status"
    pages_scanned = "pages_scanned"
    crawl_error_code = "crawl_error_code"
    crawl_error_message = "crawl_error_message"
    
    # AM-AV: Contact Extraction (10)
    phone_number = "phone_number"
    phone_source_url = "phone_source_url"
    phone_confidence = "phone_confidence"
    official_email = "official_email"
    email_source_url = "email_source_url"
    email_confidence = "email_confidence"
    contact_form_url = "contact_form_url"
    contact_form_status = "contact_form_status"
    contact_form_required_fields = "contact_form_required_fields"
    contact_evidence_summary = "contact_evidence_summary"
    
    # AW-BG: Validation & Outreach (11)
    email_validation_status = "email_validation_status"
    email_validation_score = "email_validation_score"
    email_validation_provider = "email_validation_provider"
    email_validation_at = "email_validation_at"
    email_sendable = "email_sendable"
    form_sendable = "form_sendable"
    preferred_outreach_channel = "preferred_outreach_channel"
    contactability_status = "contactability_status"
    outreach_ready = "outreach_ready"
    outreach_block_reason = "outreach_block_reason"
    next_action = "next_action"
    
    # BH-BP: Sales Execution Summary (9)
    last_contacted_at = "last_contacted_at"
    last_contact_channel = "last_contact_channel"
    last_contact_result = "last_contact_result"
    email_contact_count = "email_contact_count"
    form_contact_count = "form_contact_count"
    reply_count = "reply_count"
    last_reply_at = "last_reply_at"
    deal_status = "deal_status"
    next_contact_at = "next_contact_at"
    
    # BQ-BU: Audit (5)
    identity_confidence = "identity_confidence"
    primary_source_type = "primary_source_type"
    primary_source_ref = "primary_source_ref"
    created_at = "created_at"
    updated_at = "updated_at"
    
    @classmethod
    def all_columns(cls):
        """Return list of all column names in order."""
        return [
            # A-L
            cls.lead_id, cls.record_status, cls.lead_stage, cls.canonical_company_name,
            cls.corp_type, cls.industry, cls.company_prefecture, cls.owner,
            cls.lead_rank, cls.ng_flag, cls.sales_status, cls.memo,
            # M-T
            cls.youtube_channel_id, cls.youtube_channel_url, cls.youtube_channel_name,
            cls.youtube_handle, cls.youtube_description, cls.youtube_external_links,
            cls.youtube_discovered_at, cls.youtube_scrape_status,
            # U-AC
            cls.official_url, cls.official_domain, cls.official_site_status,
            cls.official_company_name, cls.official_company_name_source_url,
            cls.company_address, cls.source_type, cls.source_name, cls.source_url,
            # AD-AL
            cls.crawl_enabled, cls.crawl_scope, cls.crawl_target_pages,
            cls.crawl_priority, cls.last_crawled_at, cls.crawl_status,
            cls.pages_scanned, cls.crawl_error_code, cls.crawl_error_message,
            # AM-AV
            cls.phone_number, cls.phone_source_url, cls.phone_confidence,
            cls.official_email, cls.email_source_url, cls.email_confidence,
            cls.contact_form_url, cls.contact_form_status, cls.contact_form_required_fields,
            cls.contact_evidence_summary,
            # AW-BG
            cls.email_validation_status, cls.email_validation_score,
            cls.email_validation_provider, cls.email_validation_at,
            cls.email_sendable, cls.form_sendable, cls.preferred_outreach_channel,
            cls.contactability_status, cls.outreach_ready, cls.outreach_block_reason,
            cls.next_action,
            # BH-BP
            cls.last_contacted_at, cls.last_contact_channel, cls.last_contact_result,
            cls.email_contact_count, cls.form_contact_count, cls.reply_count,
            cls.last_reply_at, cls.deal_status, cls.next_contact_at,
            # BQ-BU
            cls.identity_confidence, cls.primary_source_type, cls.primary_source_ref,
            cls.created_at, cls.updated_at,
        ]
