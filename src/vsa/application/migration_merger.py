"""
Phase 1 データマージモジュール

マッチングされた複数リードを、優先度ルールに基づいてマージする。

優先度ルール:
- canonical_company_name: official_site > CRM > YouTube
- official_url: 手動確定 > 検証済み > 候補
- phone_number, email, contact_form_url: official_site pipeline のみ採用
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

from vsa.application.migration_matcher import MatchGroup
from vsa.domain.models import MasterLead
from vsa.shared.enums import (
    RecordStatus, LeadStage, OfficialSiteStatus, SourceType,
    CrawlStatus, ContactabilityStatus, OutreachBlockReason,
)

logger = structlog.get_logger(__name__)

class MergeRules:
    """マージ優先度ルール"""
    
    # データソースの信頼度（高いほど優先）
    SOURCE_PRIORITY = {
        'manual': 4,           # 手動入力
        'crm': 3,              # CRM（確認済み）
        'phase5_db': 2,        # official site pipeline
        'phase5_sheet': 1,     # Sheet（自動入力）
        'other': 0,            # その他
    }
    
    # オフィシャルサイト status の信頼度
    SITE_STATUS_PRIORITY = {
        'verified': 3,
        'not_checked': 2,
        'unverified': 1,
        'no_official_site': 0,
    }

class MigrationMerger:
    """マッチングされたリードをマージするクラス"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
    
    def merge_match_groups(self, match_groups: List[MatchGroup]) -> List[MasterLead]:
        """
        MatchGroup リストを MasterLead にマージして返す
        
        Args:
            match_groups: MatchGroup リスト
            
        Returns:
            MasterLead リスト
        """
        master_leads = []
        
        for group in match_groups:
            try:
                merged_lead = self._merge_group(group)
                if merged_lead:
                    master_leads.append(merged_lead)
            except Exception as e:
                self.logger.error("Merge failed", group_id=group.group_id, error=str(e))
        
        self.logger.info("Groups merged", total=len(match_groups), success=len(master_leads))
        
        return master_leads
    
    def _merge_group(self, group: MatchGroup) -> Optional[MasterLead]:
        """
        1 つの MatchGroup をマージして MasterLead に変換
        
        Args:
            group: MatchGroup
            
        Returns:
            MasterLead or None
        """
        if not group.leads:
            return None
        
        # グループ内で最も信頼度の高い値を各フィールドから選ぶ
        merged = self._select_best_values(group.leads)
        
        # MasterLead インスタンスを生成
        lead = MasterLead(
            lead_id=merged.get('lead_id', f"PHASE1_{group.group_id}"),
            record_status=merged.get('record_status', RecordStatus.ACTIVE),
            lead_stage=merged.get('lead_stage', LeadStage.DISCOVERED_FROM_YOUTUBE),
            canonical_company_name=merged.get('canonical_company_name', 'Unknown'),
            official_url=merged.get('official_url'),
            official_domain=merged.get('official_domain'),
            official_site_status=merged.get('official_site_status', OfficialSiteStatus.NOT_CHECKED),
            official_company_name=merged.get('official_company_name'),
            company_address=merged.get('company_address'),
            source_type=merged.get('source_type', SourceType.OTHER),
            source_name=merged.get('source_name'),
            source_url=merged.get('source_url'),
            phone_number=merged.get('phone_number'),
            official_email=merged.get('official_email'),
            crawl_status=merged.get('crawl_status', CrawlStatus.NOT_STARTED),
            primary_source_type=merged.get('primary_source_type', SourceType.OTHER),
            created_at=merged.get('created_at', datetime.now()),
            updated_at=merged.get('updated_at', datetime.now()),
            ng_flag=False,
            outreach_ready=False,
            outreach_block_reason=OutreachBlockReason.NONE,
            contactability_status=ContactabilityStatus.UNKNOWN,
        )
        
        return lead
    
    def _select_best_values(self, leads: List[Dict]) -> Dict[str, Any]:
        """
        複数リードから各フィールドの最良値を選択
        
        優先度ルール:
        - official_url: 手動 > verified > candidate
        - phone_number, email: official_site のみ
        - company_name: official_site > CRM > その他
        
        Args:
            leads: 正規化されたリード dict リスト
            
        Returns:
            マージされたデータ dict
        """
        merged = {}
        
        # canonical_company_name: official_site > CRM > その他
        merged['canonical_company_name'] = self._select_best_company_name(leads)
        
        # official_url: 手動 > verified > candidate
        merged['official_url'] = self._select_best_url(leads)
        
        # official_domain: url から抽出
        if merged['official_url']:
            from vsa.application.migration_normalizer import URLNormalizer
            merged['official_domain'] = URLNormalizer.extract_domain(merged['official_url'])
        else:
            merged['official_domain'] = None
        
        # phone_number, email: official_site pipeline のみ
        merged['phone_number'] = self._select_contact_field(leads, 'phone_number')
        merged['official_email'] = self._select_contact_field(leads, 'official_email')
        
        # official_company_name: 最初の non-null
        merged['official_company_name'] = next(
            (l.get('official_company_name') for l in leads if l.get('official_company_name')),
            None
        )
        
        # source_type, created_at: 最初のデータソースを採用
        if leads:
            merged['source_type'] = leads[0].get('source_type')
            merged['created_at'] = leads[0].get('created_at')
        
        merged['updated_at'] = datetime.now()
        merged['record_status'] = RecordStatus.ACTIVE
        merged['lead_stage'] = LeadStage.DISCOVERED_FROM_YOUTUBE
        
        return merged
    
    def _select_best_company_name(self, leads: List[Dict]) -> str:
        """
        複数リードから最良の company_name を選択
        
        優先度: official_site > CRM > その他
        
        Args:
            leads: リスト
            
        Returns:
            company_name
        """
        # official_site (phase5_db) を優先
        for lead in leads:
            source_type = lead.get('source_type')
            company = lead.get('official_company_name') or lead.get('canonical_company_name')
            if source_type == SourceType.OFFICIAL_SITE and company:
                return company
        
        # CRM を次点
        for lead in leads:
            source_type = lead.get('source_type')
            company = lead.get('official_company_name') or lead.get('canonical_company_name')
            if source_type == SourceType.CRM and company:
                return company
        
        # その他
        for lead in leads:
            company = lead.get('official_company_name') or lead.get('canonical_company_name')
            if company:
                return company
        
        return 'Unknown'
    
    def _select_best_url(self, leads: List[Dict]) -> Optional[str]:
        """
        複数リードから最良の URL を選択
        
        優先度:
        1. OfficialSiteStatus.VERIFIED
        2. 最初の non-null URL
        
        Args:
            leads: リスト
            
        Returns:
            URL
        """
        # verified URL を探す
        for lead in leads:
            if lead.get('official_site_status') == OfficialSiteStatus.VERIFIED:
                url = lead.get('official_url')
                if url:
                    return url
        
        # 最初の non-null URL を採用
        for lead in leads:
            url = lead.get('official_url')
            if url:
                return url
        
        return None
    
    def _select_contact_field(self, leads: List[Dict], field_name: str) -> Optional[str]:
        """
        連絡先フィールド（phone_number, official_email）を選択
        
        ルール: official_site pipeline (phase5_db) のみ採用
        
        Args:
            leads: リスト
            field_name: 'phone_number' or 'official_email'
            
        Returns:
            フィールド値
        """
        for lead in leads:
            source_type = lead.get('source_type')
            # phase5_db = OFFICIAL_SITE
            if source_type == SourceType.OFFICIAL_SITE:
                value = lead.get(field_name)
                if value:
                    return value
        
        return None
    
    def validate_merged_leads(self, leads: List[MasterLead]) -> Dict[str, int]:
        """
        マージされたリードの基本的な検証
        
        Returns:
            {key: count, ...}
        """
        stats = {
            'total': len(leads),
            'with_url': 0,
            'with_email': 0,
            'with_phone': 0,
            'outreach_ready': 0,
            'ng_flag': 0,
        }
        
        for lead in leads:
            if lead.official_url:
                stats['with_url'] += 1
            if lead.official_email:
                stats['with_email'] += 1
            if lead.phone_number:
                stats['with_phone'] += 1
            if lead.outreach_ready:
                stats['outreach_ready'] += 1
            if lead.ng_flag:
                stats['ng_flag'] += 1
        
        self.logger.info("Merged leads validated", stats=stats)
        
        return stats
