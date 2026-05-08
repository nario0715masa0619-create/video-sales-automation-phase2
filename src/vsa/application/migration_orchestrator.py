"""
Migration Orchestrator

Phase 1 のすべてのデータソースから Master Leads への統合マイグレーションを
一括で実行するメインモジュール。

実行フロー:
1. Extract: Phase 1 (CRM, Phase 5 Sheet, Phase 5 DB) からデータ抽出
2. Normalize: URL 正規化、Enum マッピング、"None" 除去
3. Match: 重複リード検出
4. Merge: 優先度ルールに基づいて統合
5. Load: Master Leads (Google Sheets) に書き込み
6. Validate: 統計レポート出力
"""

from typing import List, Optional, Dict
from datetime import datetime
import structlog

from vsa.config.settings import Settings
from vsa.application.migration_extractor import Phase1DataExtractor
from vsa.application.migration_normalizer import MigrationNormalizer
from vsa.application.migration_matcher import MigrationMatcher
from vsa.application.migration_merger import MigrationMerger
from vsa.application.migration_loader import MigrationLoader, MigrationLoaderFactory
from vsa.infrastructure.repository import MasterLeadsRepository
from vsa.domain.models import MasterLead

logger = structlog.get_logger(__name__)

class MigrationOrchestrator:
    """マイグレーション全体をオーケストレートするクラス"""
    
    def __init__(self, settings: Settings, repository: MasterLeadsRepository):
        """
        初期化
        
        Args:
            settings: Settings インスタンス
            repository: MasterLeadsRepository インスタンス
        """
        self.settings = settings
        self.repository = repository
        self.logger = structlog.get_logger(__name__)
        
        # 各モジュールを初期化
        self.extractor = Phase1DataExtractor(settings.google_service_account_json)
        self.normalizer = MigrationNormalizer()
        self.matcher = MigrationMatcher()
        self.merger = MigrationMerger()
        self.loader = MigrationLoaderFactory.create_loader(repository)
    
    def run_migration(self, mode: str = 'dry_run', 
                     crm_sheet_id: Optional[str] = None,
                     phase5_sheet_id: Optional[str] = None,
                     phase5_db_path: Optional[str] = None,
                     limit: Optional[int] = None) -> Dict:
        """
        フルマイグレーションパイプラインを実行
        
        Args:
            mode: "dry_run", "validate", "load"
            crm_sheet_id: CRM Google Sheet ID
            phase5_sheet_id: Phase 5 Google Sheet ID
            phase5_db_path: Phase 5 SQLite DB パス
            limit: 抽出上限件数（デバッグ用）
            
        Returns:
            {stage: stats, ...}
        """
        results = {
            'mode': mode,
            'started_at': datetime.now().isoformat(),
            'stages': {},
        }
        
        try:
            # ===== STAGE 1: EXTRACT =====
            self.logger.info("STAGE 1: Extracting data from Phase 1", 
                           crm_sheet_id=crm_sheet_id, phase5_sheet_id=phase5_sheet_id)
            
            phase1_leads = self.extractor.extract_all(
                crm_sheet_id=crm_sheet_id,
                phase5_sheet_id=phase5_sheet_id,
                phase5_db_path=phase5_db_path or 'logs/phase5_data.db',
                limit=limit
            )
            
            results['stages']['extract'] = {
                'count': len(phase1_leads),
                'status': 'success'
            }
            self.logger.info("STAGE 1 COMPLETE", count=len(phase1_leads))
            
            # ===== STAGE 2: NORMALIZE =====
            self.logger.info("STAGE 2: Normalizing data")
            
            normalized_leads = self.normalizer.normalize_batch(phase1_leads)
            
            results['stages']['normalize'] = {
                'count': len(normalized_leads),
                'status': 'success'
            }
            self.logger.info("STAGE 2 COMPLETE", count=len(normalized_leads))
            
            # ===== STAGE 3: MATCH =====
            self.logger.info("STAGE 3: Matching and deduplicating")
            
            match_groups = self.matcher.match_leads(normalized_leads)
            
            results['stages']['match'] = {
                'count': len(match_groups),
                'duplicates': len([g for g in match_groups if len(g.leads) > 1]),
                'status': 'success'
            }
            self.logger.info("STAGE 3 COMPLETE", groups=len(match_groups))
            
            # ===== STAGE 4: MERGE =====
            self.logger.info("STAGE 4: Merging matched groups")
            
            merged_leads = self.merger.merge_match_groups(match_groups)
            merge_stats = self.merger.validate_merged_leads(merged_leads)
            
            results['stages']['merge'] = {
                'count': len(merged_leads),
                'stats': merge_stats,
                'status': 'success'
            }
            self.logger.info("STAGE 4 COMPLETE", count=len(merged_leads), stats=merge_stats)
            
            # ===== STAGE 5: LOAD =====
            self.logger.info("STAGE 5: Loading to Master Leads", mode=mode)
            
            load_stats = self.loader.load_leads(merged_leads, mode=mode)
            
            results['stages']['load'] = {
                'count': load_stats['success'],
                'skipped': load_stats['skipped'],
                'error': load_stats['error'],
                'status': 'success'
            }
            self.logger.info("STAGE 5 COMPLETE", stats=load_stats)
            
            # ===== GENERATE REPORT =====
            report = self.loader.generate_load_report(load_stats, mode)
            results['report'] = report
            
            results['completed_at'] = datetime.now().isoformat()
            results['overall_status'] = 'SUCCESS'
            
        except Exception as e:
            self.logger.error("Migration failed", error=str(e))
            results['overall_status'] = 'FAILED'
            results['error'] = str(e)
        
        return results
    
    def print_results(self, results: Dict):
        """
        マイグレーション結果をコンソールに出力
        
        Args:
            results: マイグレーション結果
        """
        print("\n" + "="*60)
        print("MIGRATION RESULTS")
        print("="*60)
        
        print(f"Mode: {results['mode'].upper()}")
        print(f"Status: {results['overall_status']}")
        print(f"Started: {results.get('started_at', 'N/A')}")
        print(f"Completed: {results.get('completed_at', 'N/A')}")
        
        print("\nStage Summary:")
        for stage_name, stage_result in results.get('stages', {}).items():
            status = stage_result.get('status', 'UNKNOWN')
            count = stage_result.get('count', 0)
            print(f"  {stage_name.upper():12} {status:10} (count: {count})")
        
        if 'report' in results:
            print(results['report'])
        
        if results.get('overall_status') == 'FAILED':
            print(f"\nError: {results.get('error')}")
        
        print("="*60 + "\n")

class MigrationPipeline:
    """マイグレーション実行用ヘルパークラス"""
    
    def __init__(self, settings: Settings, repository: MasterLeadsRepository):
        """
        初期化
        
        Args:
            settings: Settings
            repository: MasterLeadsRepository
        """
        self.orchestrator = MigrationOrchestrator(settings, repository)
    
    def dry_run(self, crm_sheet_id: str, phase5_sheet_id: str, 
               phase5_db_path: str, limit: Optional[int] = None) -> Dict:
        """
        ドライラン（検証のみ）
        
        Args:
            crm_sheet_id: CRM Sheet ID
            phase5_sheet_id: Phase 5 Sheet ID
            phase5_db_path: Phase 5 DB パス
            limit: 抽出上限
            
        Returns:
            マイグレーション結果
        """
        return self.orchestrator.run_migration(
            mode='dry_run',
            crm_sheet_id=crm_sheet_id,
            phase5_sheet_id=phase5_sheet_id,
            phase5_db_path=phase5_db_path,
            limit=limit
        )
    
    def validate(self, crm_sheet_id: str, phase5_sheet_id: str,
                phase5_db_path: str, limit: Optional[int] = None) -> Dict:
        """
        前検証パス
        
        Args:
            crm_sheet_id: CRM Sheet ID
            phase5_sheet_id: Phase 5 Sheet ID
            phase5_db_path: Phase 5 DB パス
            limit: 抽出上限
            
        Returns:
            マイグレーション結果
        """
        return self.orchestrator.run_migration(
            mode='validate',
            crm_sheet_id=crm_sheet_id,
            phase5_sheet_id=phase5_sheet_id,
            phase5_db_path=phase5_db_path,
            limit=limit
        )
    
    def load(self, crm_sheet_id: str, phase5_sheet_id: str,
            phase5_db_path: str, limit: Optional[int] = None) -> Dict:
        """
        本番ロード
        
        Args:
            crm_sheet_id: CRM Sheet ID
            phase5_sheet_id: Phase 5 Sheet ID
            phase5_db_path: Phase 5 DB パス
            limit: 抽出上限
            
        Returns:
            マイグレーション結果
        """
        return self.orchestrator.run_migration(
            mode='load',
            crm_sheet_id=crm_sheet_id,
            phase5_sheet_id=phase5_sheet_id,
            phase5_db_path=phase5_db_path,
            limit=limit
        )
