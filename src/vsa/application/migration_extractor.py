"""
Phase 1 データ抽出モジュール

CRM シート、Phase 5 シート、SQLite DB から
マイグレーション対象のデータを抽出する。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import sqlite3
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class Phase1Lead:
    """Phase 1 から抽出された生データ"""
    company_name: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    source_page: Optional[str] = None
    status: Optional[str] = None
    scraped_at: Optional[str] = None
    source: str = "unknown"  # "crm", "phase5_sheet", "phase5_db"
    row_index: Optional[int] = None

class Phase1DataExtractor:
    """Phase 1 データを抽出するクラス"""
    
    def __init__(self, credentials_file: str):
        """
        初期化
        
        Args:
            credentials_file: Google Service Account JSON ファイルパス
        """
        self.credentials_file = credentials_file
        self.logger = structlog.get_logger(__name__)
    
    def extract_from_crm(self, crm_sheet_id: str, limit: Optional[int] = None) -> List[Phase1Lead]:
        """
        CRM シートからデータを抽出
        
        Args:
            crm_sheet_id: CRM Google Sheet ID
            limit: 抽出上限件数（None = 全件）
            
        Returns:
            Phase1Lead リスト
        """
        self.logger.info("Extracting from CRM Sheet", sheet_id=crm_sheet_id, limit=limit)
        # TODO: Google Sheets API を使用して CRM データを読み込み
        # 列: A=company_name, B=website_url, C=email, Z=send_count, AA～AE=send_history
        return []
    
    def extract_from_phase5_sheet(self, phase5_sheet_id: str, limit: Optional[int] = None) -> List[Phase1Lead]:
        """
        Phase 5 シートからデータを抽出
        
        Args:
            phase5_sheet_id: Phase 5 Google Sheet ID
            limit: 抽出上限件数（None = 全件）
            
        Returns:
            Phase1Lead リスト
        """
        self.logger.info("Extracting from Phase 5 Sheet", sheet_id=phase5_sheet_id, limit=limit)
        # TODO: Google Sheets API を使用して Phase 5 データを読み込み
        # 列: A=company_name, B=website_url, C=phone_number, D=email, E=source_page, F=status, G=scraped_at
        return []
    
    def extract_from_phase5_db(self, db_path: str, limit: Optional[int] = None) -> List[Phase1Lead]:
        """
        SQLite DB (phase5_data.db) からデータを抽出
        
        Args:
            db_path: phase5_data.db ファイルパス
            limit: 抽出上限件数（None = 全件）
            
        Returns:
            Phase1Lead リスト
        """
        self.logger.info("Extracting from Phase 5 DB", db_path=db_path, limit=limit)
        
        leads = []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # テーブル名を検出
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            self.logger.info("Found tables", tables=[t[0] for t in tables])
            
            # phase5_data テーブルを検索
            table_name = None
            for t in tables:
                if 'phase5' in t[0].lower():
                    table_name = t[0]
                    break
            
            if not table_name:
                self.logger.warning("No phase5 table found in DB")
                return []
            
            # データを抽出
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                lead = Phase1Lead(
                    company_name=row.get('company_name') if 'company_name' in row.keys() else None,
                    website_url=row.get('url') or row.get('website_url'),
                    email=row.get('email'),
                    phone_number=row.get('phone_number'),
                    status=row.get('status'),
                    scraped_at=row.get('scraped_at'),
                    source="phase5_db",
                    row_index=row.get('id'),
                )
                leads.append(lead)
            
            conn.close()
            self.logger.info("Extracted from DB", count=len(leads))
            
        except sqlite3.Error as e:
            self.logger.error("DB extraction failed", error=str(e))
        
        return leads
    
    def extract_all(self, crm_sheet_id: str, phase5_sheet_id: str, phase5_db_path: str, 
                   limit: Optional[int] = None) -> List[Phase1Lead]:
        """
        全データソースから抽出
        
        Args:
            crm_sheet_id: CRM Google Sheet ID
            phase5_sheet_id: Phase 5 Sheet ID
            phase5_db_path: Phase 5 DB パス
            limit: 1 つのソースあたりの抽出上限
            
        Returns:
            統合された Phase1Lead リスト
        """
        all_leads = []
        
        # CRM から抽出
        crm_leads = self.extract_from_crm(crm_sheet_id, limit)
        all_leads.extend(crm_leads)
        
        # Phase 5 Sheet から抽出
        phase5_sheet_leads = self.extract_from_phase5_sheet(phase5_sheet_id, limit)
        all_leads.extend(phase5_sheet_leads)
        
        # Phase 5 DB から抽出
        phase5_db_leads = self.extract_from_phase5_db(phase5_db_path, limit)
        all_leads.extend(phase5_db_leads)
        
        self.logger.info("Total leads extracted", count=len(all_leads),
                        crm=len(crm_leads), phase5_sheet=len(phase5_sheet_leads),
                        phase5_db=len(phase5_db_leads))
        
        return all_leads
