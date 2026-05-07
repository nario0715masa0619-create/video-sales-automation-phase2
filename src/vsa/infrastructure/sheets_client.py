from typing import List, Dict, Any, Optional
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class GoogleSheetsClient:
    """Google Sheets API クライアント"""

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, sheet_id: str, credentials_file: Optional[str] = None):
        """
        初期化
        
        Args:
            sheet_id: Google Spreadsheet ID
            credentials_file: Google Credentials JSON ファイルパス
        """
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
        self._service = None

    def _get_service(self):
        """Google Sheets API サービスを取得"""
        if self._service is None:
            if self.credentials_file:
                credentials = Credentials.from_service_account_file(
                    self.credentials_file, scopes=self.SCOPES
                )
            else:
                from google.auth import default
                credentials, _ = default(scopes=self.SCOPES)
            
            self._service = build("sheets", "v4", credentials=credentials)
        
        return self._service

    def read_range(self, sheet_name: str, range_notation: str) -> List[List[Any]]:
        """
        指定範囲のデータを読み込み
        
        Args:
            sheet_name: シート名
            range_notation: A1:Z100 形式の範囲指定
            
        Returns:
            2次元配列のデータ
        """
        service = self._get_service()
        range_name = f"{sheet_name}!{range_notation}"
        
        result = service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, range=range_name
        ).execute()
        
        return result.get("values", [])

    def write_range(
        self, 
        sheet_name: str, 
        range_notation: str, 
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """
        指定範囲にデータを書き込み
        
        Args:
            sheet_name: シート名
            range_notation: A1:Z100 形式の範囲指定
            values: 2次元配列のデータ
            
        Returns:
            API レスポンス
        """
        service = self._get_service()
        range_name = f"{sheet_name}!{range_notation}"
        
        body = {"values": values}
        
        result = service.spreadsheets().values().update(
            spreadsheetId=self.sheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body,
        ).execute()
        
        return result

    def append_rows(
        self,
        sheet_name: str,
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """
        シートの最後に行を追加
        
        Args:
            sheet_name: シート名
            values: 2次元配列のデータ
            
        Returns:
            API レスポンス
        """
        service = self._get_service()
        range_name = f"{sheet_name}!A:Z"
        
        body = {"values": values}
        
        result = service.spreadsheets().values().append(
            spreadsheetId=self.sheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body,
        ).execute()
        
        return result

    def get_sheet_metadata(self) -> Dict[str, Any]:
        """
        スプレッドシートのメタデータを取得
        
        Returns:
            メタデータ (シート名、列数など)
        """
        service = self._get_service()
        
        result = service.spreadsheets().get(
            spreadsheetId=self.sheet_id
        ).execute()
        
        return result
