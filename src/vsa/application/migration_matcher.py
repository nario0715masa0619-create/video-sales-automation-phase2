"""
Phase 1 データ照合モジュール

複数データソースから抽出されたリードを照合して、重複を検出し、統合対象を特定する。

照合キーの優先順:
1. official_domain（最も信頼度高）
2. official_url の完全一致
3. company_name + official_domain
4. company_name + official_url
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class MatchGroup:
    """マッチした複数リードのグループ"""
    group_id: str
    leads: List[Dict]  # 正規化されたリード
    match_key: str  # "domain", "url", "company+domain", "company+url"
    confidence: float  # 0.0 ~ 1.0

class MigrationMatcher:
    """Phase 1 リード照合エンジン"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
    
    def match_leads(self, normalized_leads: List[Dict]) -> List[MatchGroup]:
        """
        正規化されたリードを照合して、MatchGroup リストを返す
        
        照合ロジック:
        1. official_domain でグループ化
        2. 同じドメイン内で official_url でマッチ
        3. company_name + domain でマッチ
        4. マッチしないリードは単独グループ
        
        Args:
            normalized_leads: 正規化されたリード dict リスト
            
        Returns:
            MatchGroup リスト
        """
        if not normalized_leads:
            return []
        
        match_groups = []
        grouped = {}  # domain → [leads]
        ungrouped = []
        
        # ステップ 1: official_domain でグループ化
        for i, lead in enumerate(normalized_leads):
            domain = lead.get('official_domain')
            
            if domain:
                if domain not in grouped:
                    grouped[domain] = []
                grouped[domain].append((i, lead))
            else:
                ungrouped.append((i, lead))
        
        # ステップ 2: domain ベースのグループから MatchGroup を生成
        group_id_counter = 0
        for domain, leads_with_idx in grouped.items():
            if len(leads_with_idx) == 1:
                # 単独リード
                _, lead = leads_with_idx[0]
                match_groups.append(MatchGroup(
                    group_id=f"domain_{group_id_counter}",
                    leads=[lead],
                    match_key="domain",
                    confidence=0.9  # domain は信頼度高
                ))
            else:
                # 複数リード - さらに細分化
                subgroups = self._match_within_domain(leads_with_idx)
                for subgroup in subgroups:
                    match_groups.append(MatchGroup(
                        group_id=f"domain_{group_id_counter}",
                        leads=subgroup,
                        match_key="url_or_company",
                        confidence=0.8
                    ))
            
            group_id_counter += 1
        
        # ステップ 3: ungrouped (ドメインなし) リードを処理
        for idx, lead in ungrouped:
            match_groups.append(MatchGroup(
                group_id=f"ungrouped_{idx}",
                leads=[lead],
                match_key="none",
                confidence=0.3  # ドメイン不明 → 信頼度低
            ))
        
        self.logger.info("Leads matched", total=len(normalized_leads),
                        groups=len(match_groups), domain_groups=len(grouped),
                        ungrouped=len(ungrouped))
        
        return match_groups
    
    def _match_within_domain(self, leads_with_idx: List[Tuple[int, Dict]]) -> List[List[Dict]]:
        """
        同一ドメイン内でさらに細かく照合
        
        Args:
            leads_with_idx: [(index, lead), ...] のリスト
            
        Returns:
            [[lead, lead, ...], ...] のリスト（各要素がマッチした複数リード）
        """
        subgroups = []
        matched_indices = set()
        
        for i, (idx1, lead1) in enumerate(leads_with_idx):
            if idx1 in matched_indices:
                continue
            
            subgroup = [lead1]
            matched_indices.add(idx1)
            
            # lead1 とマッチするリードを探す
            for j, (idx2, lead2) in enumerate(leads_with_idx):
                if j <= i or idx2 in matched_indices:
                    continue
                
                if self._leads_match(lead1, lead2):
                    subgroup.append(lead2)
                    matched_indices.add(idx2)
            
            subgroups.append(subgroup)
        
        return subgroups
    
    def _leads_match(self, lead1: Dict, lead2: Dict) -> bool:
        """
        2 つのリードがマッチするか判定
        
        マッチルール:
        - official_url が同じ
        - company_name が同じ（かつ非空）
        
        Args:
            lead1, lead2: 正規化されたリード dict
            
        Returns:
            True if match
        """
        # URL で比較
        url1 = lead1.get('official_url')
        url2 = lead2.get('official_url')
        if url1 and url2 and url1 == url2:
            return True
        
        # company_name で比較（空文字列は除外）
        company1 = lead1.get('official_company_name', '').strip()
        company2 = lead2.get('official_company_name', '').strip()
        if company1 and company2 and company1.lower() == company2.lower():
            return True
        
        return False
    
    def detect_duplicates(self, match_groups: List[MatchGroup]) -> Dict[str, List[int]]:
        """
        MatchGroup 内で重複リードを検出
        
        Returns:
            {group_id: [duplicate_indices], ...}
        """
        duplicates = {}
        
        for group in match_groups:
            if len(group.leads) > 1:
                # 複数リードがグループ化されている = 重複候補
                duplicates[group.group_id] = list(range(len(group.leads)))
        
        self.logger.info("Duplicates detected", count=len(duplicates),
                        total_duplicate_records=sum(len(v) for v in duplicates.values()))
        
        return duplicates
