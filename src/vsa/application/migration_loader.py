"""
Phase 2 Master Leads ローダーモジュール

マージされた MasterLead リストを Google Sheets Master Leads に書き込む。

モード:
- dry_run: 検証のみ、実際には書き込まない
- validate: 前検証パス
- load: 本番書き込み
"""

from typing import List, Dict, Optional
from datetime import datetime
import structlog

from vsa.domain.models import MasterLead
from vsa.infrastructure.converters import RowToModelConverter
from vsa.infrastructure.repository import MasterLeadsRepository
from vsa.shared.constants import MasterLeadsColumns

logger = structlog.get_logger(__name__)

class MigrationLoader:
    """Master Leads へのデータロード"""
    
    def __init__(self, repository: MasterLeadsRepository):
        """
        初期化
        
        Args:
            repository: MasterLeadsRepository インスタンス
        """
        self.repository = repository
        self.logger = structlog.get_logger(__name__)
    
    def load_leads(self, leads: List[MasterLead], mode: str = 'dry_run') -> Dict[str, int]:
        """
        MasterLead リストを Master Leads に書き込む
        
        Args:
            leads: MasterLead リスト
            mode: "dry_run" (検証のみ), "validate" (前検証), "load" (本番)
            
        Returns:
            {status: count, ...}
        """
        if mode not in ('dry_run', 'validate', 'load'):
            raise ValueError(f"Invalid mode: {mode}")
        
        stats = {
            'total': len(leads),
            'success': 0,
            'skipped': 0,
            'error': 0,
        }
        
        if mode == 'dry_run':
            self.logger.info("DRY RUN MODE: No actual writes", count=len(leads))
            for lead in leads:
                self._validate_lead(lead)
                stats['success'] += 1
            return stats
        
        if mode == 'validate':
            self.logger.info("VALIDATE MODE: Pre-validation check", count=len(leads))
            for lead in leads:
                if self._validate_lead(lead):
                    stats['success'] += 1
                else:
                    stats['error'] += 1
            return stats
        
        if mode == 'load':
            self.logger.info("LOAD MODE: Writing to Master Leads", count=len(leads))
            for i, lead in enumerate(leads):
                try:
                    if not self._validate_lead(lead):
                        self.logger.warning("Lead validation failed, skipping", lead_id=lead.lead_id)
                        stats['skipped'] += 1
                        continue
                    
                    # リポジトリに保存
                    self.repository.save(lead)
                    stats['success'] += 1
                    
                    if (i + 1) % 100 == 0:
                        self.logger.info("Progress", loaded=i + 1, total=len(leads))
                    
                except Exception as e:
                    self.logger.error("Load failed", lead_id=lead.lead_id, error=str(e))
                    stats['error'] += 1
            
            self.logger.info("Load completed", stats=stats)
            return stats
    
    def _validate_lead(self, lead: MasterLead) -> bool:
        """
        MasterLead の基本的なバリデーション
        
        チェック項目:
        - lead_id が空でない
        - canonical_company_name が空でない
        - 必須フィールドが有効な型
        
        Args:
            lead: MasterLead
            
        Returns:
            True if valid
        """
        if not lead.lead_id or not lead.lead_id.strip():
            self.logger.warning("Validation failed: missing lead_id")
            return False
        
        if not lead.canonical_company_name or not lead.canonical_company_name.strip():
            self.logger.warning("Validation failed: missing canonical_company_name", lead_id=lead.lead_id)
            return False
        
        # 型チェック（基本）
        if not isinstance(lead.ng_flag, bool):
            self.logger.warning("Validation failed: ng_flag must be bool", lead_id=lead.lead_id)
            return False
        
        return True
    
    def generate_load_report(self, stats: Dict[str, int], mode: str) -> str:
        """
        ロード統計レポートを生成
        
        Args:
            stats: ロード統計
            mode: "dry_run", "validate", "load"
            
        Returns:
            レポート文字列
        """
        report = f"""
================================================
Migration Load Report
================================================
Mode: {mode.upper()}
Timestamp: {datetime.now().isoformat()}

Statistics:
  Total Leads: {stats['total']}
  Success: {stats['success']}
  Skipped: {stats['skipped']}
  Error: {stats['error']}

Success Rate: {stats['success'] / max(stats['total'], 1) * 100:.1f}%

Next Steps:
"""
        
        if mode == 'dry_run':
            report += """
  1. Review the validation results above
  2. If OK, run with mode='validate'
  3. If validation passes, run with mode='load'
"""
        elif mode == 'validate':
            report += """
  1. Review validation errors (if any)
  2. Fix issues in migration normalizer/matcher/merger
  3. Re-run with mode='validate'
  4. Once all pass, run with mode='load'
"""
        elif mode == 'load':
            report += """
  1. Verify loaded data in Master Leads sheet
  2. Check for any orphaned or incomplete records
  3. Run deduplication (if needed)
  4. Proceed to next migration phase
"""
        
        report += """
================================================
"""
        return report

class MigrationLoaderFactory:
    """ローダーファクトリー（dependency injection）"""
    
    @staticmethod
    def create_loader(repository: MasterLeadsRepository) -> MigrationLoader:
        """
        MigrationLoader インスタンスを生成
        
        Args:
            repository: MasterLeadsRepository
            
        Returns:
            MigrationLoader
        """
        return MigrationLoader(repository)
