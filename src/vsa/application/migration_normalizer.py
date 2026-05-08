"""
Phase 1 データ正規化モジュール

抽出したデータを以下の通り正規化:
- URL 正規化 (https 優先、末尾スラッシュ削除)
- Enum マッピング (文字列 → Python Enum)
- "None" 文字列 → None (Python null)
- 日時形式統一 (ISO format)
- 空白トリミング
- 重複除去
"""

from typing import Optional, Dict, Any
from urllib.parse import urlparse, urlunparse
from datetime import datetime
import re
import structlog

from vsa.shared.enums import (
    RecordStatus, LeadStage, SourceType, OfficialSiteStatus,
    CrawlStatus, EmailValidationStatus, ContactabilityStatus,
    DealStatus, SalesStatus, LeadRank,
)
from vsa.application.migration_extractor import Phase1Lead

logger = structlog.get_logger(__name__)

class URLNormalizer:
    """URL 正規化ユーティリティ"""
    
    @staticmethod
    def normalize(url: Optional[str]) -> Optional[str]:
        """
        URL を正規化
        
        Rules:
        - https:// 優先
        - www. プリフィックスは保持
        - クエリパラメータ削除
        - フラグメント削除
        - 末尾スラッシュ削除
        - スペース削除
        - 小文字化
        
        Args:
            url: 入力 URL
            
        Returns:
            正規化された URL または None
        """
        if not url or not isinstance(url, str):
            return None
        
        url = url.strip()
        if not url:
            return None
        
        # プロトコルがない場合は https:// を追加
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            
            # http を https に統一
            scheme = 'https' if parsed.scheme in ('http', 'https') else parsed.scheme
            netloc = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # パスから末尾スラッシュを削除（/ のみの場合を除く）
            if path and path != '/' and path.endswith('/'):
                path = path.rstrip('/')
            
            # クエリ・フラグメント削除
            normalized = f"{scheme}://{netloc}{path}"
            
            return normalized
            
        except Exception as e:
            logger.warning("URL normalization failed", url=url, error=str(e))
            return None
    
    @staticmethod
    def extract_domain(url: Optional[str]) -> Optional[str]:
        """
        URL からドメインを抽出
        
        例: https://www.example.com/path → www.example.com
        
        Args:
            url: URL
            
        Returns:
            ドメイン
        """
        normalized = URLNormalizer.normalize(url)
        if not normalized:
            return None
        
        try:
            parsed = urlparse(normalized)
            return parsed.netloc.lower()
        except Exception as e:
            logger.warning("Domain extraction failed", url=url, error=str(e))
            return None

class EnumMapper:
    """Enum マッピングユーティリティ"""
    
    # Phase 1 ステータス → Phase 2 LeadStage マッピング
    STATUS_TO_LEAD_STAGE = {
        'success': LeadStage.VALIDATED,  # スクレイピング成功 → validated
        'ready_to_contact': LeadStage.OUTREACH_READY,
        'invalid': LeadStage.DISCOVERED_FROM_YOUTUBE,  # 失敗 → 初期段階
        'skipped': LeadStage.DISCOVERED_FROM_YOUTUBE,
    }
    
    # Phase 1 ステータス → Phase 2 CrawlStatus マッピング
    STATUS_TO_CRAWL_STATUS = {
        'success': CrawlStatus.SUCCESS,
        'invalid': CrawlStatus.FAILED,
        'skipped': CrawlStatus.SKIPPED,
    }
    
    @staticmethod
    def map_source_type(source: str) -> SourceType:
        """
        データソース文字列 → SourceType Enum
        
        Args:
            source: "crm", "phase5_sheet", "phase5_db"
            
        Returns:
            SourceType Enum
        """
        source_map = {
            'crm': SourceType.CRM,
            'phase5_sheet': SourceType.OFFICIAL_SITE,  # Sheet = 手動入力
            'phase5_db': SourceType.OFFICIAL_SITE,  # DB = スクレイピング結果
        }
        return source_map.get(source, SourceType.OTHER)
    
    @staticmethod
    def map_lead_stage(phase1_status: Optional[str], source: str) -> LeadStage:
        """
        Phase 1 status → Phase 2 LeadStage Enum
        
        Args:
            phase1_status: Phase 1 の status 値
            source: データソース
            
        Returns:
            LeadStage Enum
        """
        if not phase1_status:
            return LeadStage.DISCOVERED_FROM_YOUTUBE
        
        # status が有効な場合
        mapped = EnumMapper.STATUS_TO_LEAD_STAGE.get(phase1_status.lower())
        if mapped:
            return mapped
        
        # デフォルト
        return LeadStage.DISCOVERED_FROM_YOUTUBE

class DataNormalizer:
    """データ正規化メインクラス"""
    
    @staticmethod
    def clean_string(value: Optional[str]) -> Optional[str]:
        """
        文字列をクリーニング
        
        - スペース削除
        - "None" 文字列 → None
        - 空文字列 → None
        
        Args:
            value: 入力文字列
            
        Returns:
            クリーニング後の文字列
        """
        if not value or not isinstance(value, str):
            return None
        
        value = value.strip()
        
        # "None", "none", "N/A" 等を None に変換
        if value.lower() in ('none', 'n/a', 'null', ''):
            return None
        
        return value if value else None
    
    @staticmethod
    def parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """
        日時文字列をパース
        
        対応フォーマット:
        - ISO format: 2026-04-24T15:45:46
        - SQL format: 2026-04-24 15:45:46
        - Date only: 2026-04-24
        
        Args:
            value: 日時文字列
            
        Returns:
            datetime オブジェクト または None
        """
        value = DataNormalizer.clean_string(value)
        if not value:
            return None
        
        formats = [
            '%Y-%m-%dT%H:%M:%S',  # ISO
            '%Y-%m-%d %H:%M:%S',  # SQL
            '%Y-%m-%d',           # Date only
            '%Y/%m/%d %H:%M:%S',  # Japanese format
            '%Y/%m/%d',           # Japanese date
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        logger.warning("Failed to parse datetime", value=value)
        return None
    
    @staticmethod
    def normalize_lead(phase1_lead: Phase1Lead) -> Dict[str, Any]:
        """
        Phase1Lead を正規化して dict に変換
        
        Args:
            phase1_lead: Phase 1 リード
            
        Returns:
            正規化されたデータ dict
        """
        # URL 正規化
        official_url = URLNormalizer.normalize(phase1_lead.website_url)
        official_domain = URLNormalizer.extract_domain(official_url) if official_url else None
        
        # 文字列クリーニング
        company_name = DataNormalizer.clean_string(phase1_lead.company_name)
        phone_number = DataNormalizer.clean_string(phase1_lead.phone_number)
        official_email = DataNormalizer.clean_string(phase1_lead.email)
        
        # 日時パース
        created_at = DataNormalizer.parse_datetime(phase1_lead.scraped_at)
        
        # Enum マッピング
        source_type = EnumMapper.map_source_type(phase1_lead.source)
        lead_stage = EnumMapper.map_lead_stage(phase1_lead.status, phase1_lead.source)
        crawl_status = CrawlStatus.SUCCESS if phase1_lead.status == 'success' else CrawlStatus.FAILED
        
        # 採用ルール適用: phone_number / email は official site pipeline のみ採用
        # phase5_db は official site pipeline とみなす
        if phase1_lead.source != 'phase5_db':
            # CRM や Sheet からのデータは contact extraction に含めない
            phone_number = None
            official_email = None
        
        return {
            'lead_id': f"PHASE1_{phase1_lead.source}_{phase1_lead.row_index}" if phase1_lead.row_index else None,
            'record_status': RecordStatus.ACTIVE,
            'lead_stage': lead_stage,
            'canonical_company_name': company_name or 'Unknown',
            'official_url': official_url,
            'official_domain': official_domain,
            'official_company_name': company_name,
            'official_site_status': OfficialSiteStatus.VERIFIED if official_url else OfficialSiteStatus.NOT_CHECKED,
            'source_type': source_type,
            'phone_number': phone_number,
            'official_email': official_email,
            'crawl_status': crawl_status,
            'primary_source_type': source_type,
            'created_at': created_at or datetime.now(),
            'updated_at': datetime.now(),
        }

class MigrationNormalizer:
    """Migration データ正規化オーケストレータ"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
    
    def normalize_batch(self, phase1_leads: list) -> list:
        """
        Phase1Lead バッチを正規化
        
        Args:
            phase1_leads: Phase1Lead リスト
            
        Returns:
            正規化されたデータ dict リスト
        """
        normalized = []
        errors = []
        
        for i, lead in enumerate(phase1_leads):
            try:
                normalized_data = DataNormalizer.normalize_lead(lead)
                normalized.append(normalized_data)
            except Exception as e:
                self.logger.warning("Normalization failed", index=i, error=str(e))
                errors.append((i, str(e)))
        
        self.logger.info("Normalization completed", total=len(phase1_leads),
                        success=len(normalized), error=len(errors))
        
        return normalized
