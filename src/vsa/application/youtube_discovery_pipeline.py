"""
YouTube Discovery - Orchestrator

YouTube チャネル情報取得パイプライン全体を統合するモジュール。
"""

from typing import Optional, List
from datetime import datetime
import structlog

from vsa.domain.models import MasterLead
from vsa.shared.enums import LeadStage, YouTubeScrapeStatus
from vsa.application.youtube_api_client import YouTubeAPIClient

logger = structlog.get_logger(__name__)

class YouTubeDiscoveryPipeline:
    """YouTube チャネル情報取得パイプライン"""
    
    def __init__(self, youtube_api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            youtube_api_key: YouTube Data API キー
        """
        self.api_client = YouTubeAPIClient(youtube_api_key) if youtube_api_key else None
        self.logger = structlog.get_logger(__name__)
    
    def enrich_from_youtube(self, lead: MasterLead) -> MasterLead:
        """
        YouTube チャネル情報からリードを充実させる
        
        Args:
            lead: MasterLead
            
        Returns:
            充実した MasterLead
        """
        # YouTube チャネル ID または URL が必要
        channel_id = lead.youtube_channel_id
        channel_url = lead.youtube_channel_url
        
        if not channel_id and not channel_url:
            self.logger.info("Skipping YouTube enrichment: no channel info", 
                           lead_id=lead.lead_id)
            return lead
        
        if not self.api_client:
            self.logger.warning("YouTube API client not configured")
            return lead
        
        try:
            # API からチャネル情報を取得
            if channel_id:
                channel_info = self.api_client.get_channel_by_id(channel_id)
            else:
                channel_info = self.api_client.get_channel_by_url(channel_url)
            
            if not channel_info:
                lead.youtube_scrape_status = YouTubeScrapeStatus.FAILED
                lead.mark_updated()
                return lead
            
            # リードに情報をマップ
            lead.youtube_channel_id = channel_info.get('channel_id')
            lead.youtube_channel_name = channel_info.get('channel_name')
            lead.youtube_description = channel_info.get('description')
            
            # 外部リンク (公式サイト URL の候補) を取得
            external_links = self.api_client.get_channel_external_links(
                lead.youtube_channel_id
            )
            if external_links:
                lead.youtube_external_links = ','.join(external_links)
                
                # 公式 URL が未設定の場合、YouTube 外部リンクを候補として設定
                if not lead.official_url and external_links:
                    lead.official_url = external_links[0]
            
            # スクレイプ成功を記録
            lead.youtube_scrape_status = YouTubeScrapeStatus.SCRAPED
            lead.lead_stage = LeadStage.VALIDATED  # YouTube 情報取得済み
            lead.mark_updated()
            
            self.logger.info("YouTube enrichment completed", lead_id=lead.lead_id,
                           channel_id=channel_info.get('channel_id'),
                           external_links=len(external_links))
            
        except Exception as e:
            self.logger.error("YouTube enrichment failed", lead_id=lead.lead_id,
                            error=str(e))
            lead.youtube_scrape_status = YouTubeScrapeStatus.FAILED
            lead.mark_updated()
        
        return lead
    
    def enrich_batch(self, leads: List[MasterLead]) -> List[MasterLead]:
        """
        リードバッチを YouTube 情報で充実させる
        
        Args:
            leads: MasterLead リスト
            
        Returns:
            充実した MasterLead リスト
        """
        enriched = []
        
        for i, lead in enumerate(leads):
            try:
                enriched_lead = self.enrich_from_youtube(lead)
                enriched.append(enriched_lead)
            except Exception as e:
                self.logger.error("Batch enrichment failed", 
                                lead_id=lead.lead_id, error=str(e))
                enriched.append(lead)
            
            if (i + 1) % 10 == 0:
                self.logger.info("Progress", processed=i + 1, total=len(leads))
        
        self.logger.info("YouTube batch enrichment completed", total=len(leads))
        
        return enriched
