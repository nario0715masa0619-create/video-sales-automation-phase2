"""
Official Site Enrichment - Target Planner

クロール対象となる公式サイトのページリストを計画するモジュール。
"""

from typing import List, Optional
from enum import Enum
from dataclasses import dataclass
import structlog

from vsa.shared.enums import CrawlScope

logger = structlog.get_logger(__name__)

@dataclass
class CrawlTarget:
    """クロール対象ページ"""
    url: str
    page_type: str  # "top", "contact", "company", "legal", "privacy", "recruit", "location"
    priority: int  # 1=最高、10=最低
    scope: CrawlScope

class TargetPageDefinition:
    """各スコープでのターゲットページ定義"""
    
    # Focused スコープ (デフォルト)
    FOCUSED_PAGES = {
        'top': {'name': 'トップページ', 'priority': 1},
        'contact': {'name': '問い合わせページ', 'priority': 2},
        'company': {'name': '会社概要ページ', 'priority': 3},
        'legal': {'name': '特定商取引ページ', 'priority': 4},
        'privacy': {'name': 'プライバシーポリシー', 'priority': 5},
        'recruit': {'name': '採用情報ページ', 'priority': 6},
        'location': {'name': '所在地・アクセスページ', 'priority': 7},
    }
    
    # Standard スコープ
    STANDARD_PAGES = dict(FOCUSED_PAGES)
    STANDARD_PAGES.update({
        'service': {'name': 'サービス一覧ページ', 'priority': 8},
        'business': {'name': 'ビジネス紹介ページ', 'priority': 9},
        'faq_contact': {'name': 'FAQ・問い合わせページ', 'priority': 10},
    })
    
    # Deep スコープ (フルクロール - 制限あり)
    DEEP_PAGES = dict(STANDARD_PAGES)

class OfficialSiteTargetPlanner:
    """公式サイトのクロール対象計画"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
    
    def plan_crawl_targets(self, official_domain: str, scope: CrawlScope) -> List[CrawlTarget]:
        """
        クロール対象ページリストを計画
        
        Args:
            official_domain: official_domain (e.g., "example.com")
            scope: CrawlScope (focused, standard, deep)
            
        Returns:
            CrawlTarget リスト
        """
        if not official_domain:
            return []
        
        # ドメインから base URL を構築
        base_url = f"https://{official_domain}"
        
        # スコープに応じたページリストを取得
        if scope == CrawlScope.FOCUSED:
            pages = TargetPageDefinition.FOCUSED_PAGES
        elif scope == CrawlScope.STANDARD:
            pages = TargetPageDefinition.STANDARD_PAGES
        elif scope == CrawlScope.DEEP:
            pages = TargetPageDefinition.DEEP_PAGES
        else:
            pages = {}
        
        targets = []
        for page_type, page_info in pages.items():
            target = CrawlTarget(
                url=self._construct_page_url(base_url, page_type),
                page_type=page_type,
                priority=page_info['priority'],
                scope=scope,
            )
            targets.append(target)
        
        self.logger.info("Crawl targets planned", domain=official_domain,
                        scope=scope.value, count=len(targets))
        
        return targets
    
    def _construct_page_url(self, base_url: str, page_type: str) -> str:
        """
        ページタイプから URL を構築
        
        例: https://example.com/contact/
        
        Args:
            base_url: ベース URL
            page_type: ページタイプ
            
        Returns:
            ページ URL
        """
        # これは候補 URL。実際のサイトによって異なるため、
        # クローラーが見つけられなかった場合はスキップする
        path_map = {
            'top': '/',
            'contact': '/contact/',
            'company': '/company/',
            'legal': '/legal/',
            'privacy': '/privacy/',
            'recruit': '/recruit/',
            'location': '/location/',
            'service': '/service/',
            'business': '/business/',
            'faq_contact': '/faq/',
        }
        
        path = path_map.get(page_type, '/')
        return f"{base_url}{path}"
