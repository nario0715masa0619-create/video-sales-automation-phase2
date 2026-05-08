"""
Official Site Enrichment - Orchestrator

公式サイト情報抽出パイプライン全体を統合するモジュール。
"""

from typing import Optional, Dict
from datetime import datetime
import structlog

from vsa.domain.models import MasterLead
from vsa.shared.enums import CrawlScope, CrawlStatus, PhoneConfidence, EmailConfidence, ContactFormStatus
from vsa.application.enrichment_target_planner import OfficialSiteTargetPlanner
from vsa.application.enrichment_crawler import OfficialSiteCrawler
from vsa.application.enrichment_contact_extractor import ContactExtractorOrchestrator

logger = structlog.get_logger(__name__)

class OfficialSiteEnrichmentPipeline:
    """公式サイト情報抽出パイプライン"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        初期化
        
        Args:
            timeout: クロールタイムアウト (秒)
            max_retries: リトライ回数
        """
        self.planner = OfficialSiteTargetPlanner()
        self.crawler = OfficialSiteCrawler(timeout=timeout, max_retries=max_retries)
        self.contact_extractor = ContactExtractorOrchestrator()
        self.logger = structlog.get_logger(__name__)
    
    def enrich_lead(self, lead: MasterLead) -> MasterLead:
        """
        リードの公式サイト情報を充実させる
        
        Args:
            lead: MasterLead
            
        Returns:
            充実した MasterLead
        """
        if not lead.official_domain:
            self.logger.info("Skipping enrichment: no official_domain", lead_id=lead.lead_id)
            return lead
        
        if not lead.crawl_enabled:
            self.logger.info("Crawling disabled", lead_id=lead.lead_id)
            return lead
        
        # クロール対象を計画
        scope = lead.crawl_scope or CrawlScope.FOCUSED
        targets = self.planner.plan_crawl_targets(lead.official_domain, scope)
        
        if not targets:
            return lead
        
        # クロール実行
        all_html = ""
        pages_crawled = 0
        
        for target in targets:
            html = self.crawler.crawl(target.url)
            if html:
                all_html += html
                pages_crawled += 1
        
        if pages_crawled == 0:
            lead.crawl_status = CrawlStatus.FAILED
            lead.mark_updated()
            return lead
        
        # 連絡先抽出
        contact_info = self.contact_extractor.extract_all(all_html)
        
        # リードを更新
        if contact_info.get('phone_number'):
            lead.phone_number = contact_info['phone_number']
            lead.phone_confidence = PhoneConfidence.MEDIUM
        
        if contact_info.get('official_email'):
            lead.official_email = contact_info['official_email']
            lead.email_confidence = EmailConfidence.MEDIUM
        
        if contact_info.get('contact_form_status') == 'found':
            lead.contact_form_status = ContactFormStatus.FOUND
        else:
            lead.contact_form_status = ContactFormStatus.NOT_FOUND
        
        # クロール結果を記録
        lead.crawl_status = CrawlStatus.SUCCESS
        lead.pages_scanned = pages_crawled
        lead.last_crawled_at = datetime.now()
        lead.mark_updated()
        
        self.logger.info("Enrichment completed", lead_id=lead.lead_id,
                        pages=pages_crawled, phone=bool(contact_info.get('phone_number')),
                        email=bool(contact_info.get('official_email')))
        
        return lead
    
    def enrich_batch(self, leads: list) -> list:
        """
        リードバッチを充実させる
        
        Args:
            leads: MasterLead リスト
            
        Returns:
            充実した MasterLead リスト
        """
        enriched = []
        
        for i, lead in enumerate(leads):
            try:
                enriched_lead = self.enrich_lead(lead)
                enriched.append(enriched_lead)
            except Exception as e:
                self.logger.error("Enrichment failed", lead_id=lead.lead_id, error=str(e))
                enriched.append(lead)
            
            if (i + 1) % 10 == 0:
                self.logger.info("Progress", processed=i + 1, total=len(leads))
        
        self.logger.info("Batch enrichment completed", total=len(leads))
        
        return enriched
    
    def close(self):
        """クローラーセッションをクローズ"""
        self.crawler.close()
