from typing import List, Optional
import structlog

from vsa.domain.models import MasterLead
from vsa.infrastructure.repository import MasterLeadsRepository
from vsa.infrastructure.sheets_client import GoogleSheetsClient
from vsa.infrastructure.converters import RowToModelConverter


logger = structlog.get_logger()


class GoogleSheetsRepositoryImpl(MasterLeadsRepository):
    """Google Sheets 実装 - MasterLeadsRepository"""

    def __init__(
        self,
        sheet_id: str,
        sheet_name: str = "Master Leads",
        credentials_file: Optional[str] = None,
    ):
        """
        初期化
        
        Args:
            sheet_id: Google Spreadsheet ID
            sheet_name: シート名 (デフォルト: Master Leads)
            credentials_file: Google Credentials JSON ファイルパス
        """
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.credentials_file = credentials_file
        self.client = GoogleSheetsClient(sheet_id, credentials_file)
        self._header_row = None

    def _get_header_row(self) -> List[str]:
        """ヘッダー行を取得 (キャッシュ)"""
        if self._header_row is None:
            rows = self.client.read_range(self.sheet_name, "1:1")
            if rows:
                self._header_row = rows[0]
            else:
                raise ValueError(f"Sheet '{self.sheet_name}' has no header row")
        return self._header_row

    def _rows_to_models(self, rows: List[List[str]]) -> List[MasterLead]:
        """シート行をモデルに変換"""
        header = self._get_header_row()
        models = []
        
        for row in rows:
            if not row:
                continue
            
            # 行データを辞書に変換
            row_dict = {}
            for i, header_val in enumerate(header):
                row_dict[header_val] = row[i] if i < len(row) else ""
            
            # モデルに変換
            try:
                model = RowToModelConverter.sheet_row_to_model(row_dict)
                models.append(model)
            except Exception as e:
                logger.warning(
                    "Failed to convert row to model",
                    row=row,
                    error=str(e)
                )
        
        return models

    def get_all(self) -> List[MasterLead]:
        """
        すべてのリードを取得
        
        Returns:
            MasterLead リスト
        """
        logger.info("Fetching all leads from Master Leads sheet")
        
        try:
            # ヘッダーをスキップして2行目以降を読み込み
            rows = self.client.read_range(self.sheet_name, "2:1000")
            models = self._rows_to_models(rows)
            
            logger.info(
                "Successfully fetched leads",
                count=len(models)
            )
            
            return models
        except Exception as e:
            logger.error("Failed to fetch all leads", error=str(e))
            raise

    def get_by_id(self, lead_id: str) -> Optional[MasterLead]:
        """
        ID でリードを検索
        
        Args:
            lead_id: Lead ID
            
        Returns:
            MasterLead または None
        """
        logger.info("Fetching lead by ID", lead_id=lead_id)
        
        try:
            rows = self.client.read_range(self.sheet_name, "2:1000")
            models = self._rows_to_models(rows)
            
            for model in models:
                if model.lead_id == lead_id:
                    logger.info("Found lead", lead_id=lead_id)
                    return model
            
            logger.warning("Lead not found", lead_id=lead_id)
            return None
        except Exception as e:
            logger.error("Failed to fetch lead by ID", lead_id=lead_id, error=str(e))
            raise

    def get_by_official_domain(self, domain: str) -> Optional[MasterLead]:
        """
        公式ドメインでリードを検索
        
        Args:
            domain: Official Domain
            
        Returns:
            MasterLead または None
        """
        logger.info("Fetching lead by official domain", domain=domain)
        
        try:
            rows = self.client.read_range(self.sheet_name, "2:1000")
            models = self._rows_to_models(rows)
            
            for model in models:
                if model.official_domain == domain:
                    logger.info("Found lead", domain=domain)
                    return model
            
            logger.warning("Lead not found", domain=domain)
            return None
        except Exception as e:
            logger.error("Failed to fetch lead by domain", domain=domain, error=str(e))
            raise

    def save(self, lead: MasterLead) -> None:
        """
        リードを保存 (既存なら更新、なければ追加)
        
        Args:
            lead: MasterLead モデル
        """
        logger.info("Saving lead", lead_id=lead.lead_id)
        
        try:
            # 既存リードを検索
            existing = self.get_by_id(lead.lead_id)
            
            if existing:
                self._update_lead(lead)
            else:
                self._append_lead(lead)
        except Exception as e:
            logger.error("Failed to save lead", lead_id=lead.lead_id, error=str(e))
            raise

    def _append_lead(self, lead: MasterLead) -> None:
        """新しいリードを追加"""
        row_dict = RowToModelConverter.model_to_sheet_row(lead)
        header = self._get_header_row()
        
        # ヘッダー順に値を並べる
        row_values = [[row_dict.get(h, "") for h in header]]
        
        self.client.append_rows(self.sheet_name, row_values)
        logger.info("Appended new lead", lead_id=lead.lead_id)

    def _update_lead(self, lead: MasterLead) -> None:
        """既存リードを更新"""
        # すべてのリードを取得して行番号を特定
        rows = self.client.read_range(self.sheet_name, "2:1000")
        models = self._rows_to_models(rows)
        
        for idx, model in enumerate(models):
            if model.lead_id == lead.lead_id:
                row_dict = RowToModelConverter.model_to_sheet_row(lead)
                header = self._get_header_row()
                
                row_values = [[row_dict.get(h, "") for h in header]]
                row_number = idx + 2  # ヘッダー分でoffset
                
                self.client.write_range(
                    self.sheet_name,
                    f"{row_number}:{row_number}",
                    row_values
                )
                logger.info("Updated lead", lead_id=lead.lead_id)
                return
        
        raise ValueError(f"Lead not found: {lead.lead_id}")

    def save_batch(self, leads: List[MasterLead]) -> None:
        """
        複数のリードを保存
        
        Args:
            leads: MasterLead リスト
        """
        logger.info("Saving batch of leads", count=len(leads))
        
        for lead in leads:
            self.save(lead)
        
        logger.info("Batch save completed", count=len(leads))

    def delete(self, lead_id: str) -> None:
        """
        リードを削除 (実装未定 - Sheets APIでは削除が複雑)
        
        Args:
            lead_id: Lead ID
        """
        logger.warning("Delete operation not implemented for Google Sheets")
        raise NotImplementedError("Delete operation not supported yet")
