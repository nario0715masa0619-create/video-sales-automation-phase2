from abc import ABC, abstractmethod
from typing import List, Optional
from vsa.domain.models import MasterLead

class MasterLeadsRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[MasterLead]:
        pass
    
    @abstractmethod
    def get_by_id(self, lead_id: str) -> Optional[MasterLead]:
        pass
    
    @abstractmethod
    def save(self, lead: MasterLead) -> None:
        pass

class GoogleSheetsRepository(MasterLeadsRepository):
    def __init__(self, sheet_id: str, credentials_file: Optional[str] = None):
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
    
    def get_all(self) -> List[MasterLead]:
        raise NotImplementedError()
    
    def get_by_id(self, lead_id: str) -> Optional[MasterLead]:
        raise NotImplementedError()
    
    def save(self, lead: MasterLead) -> None:
        raise NotImplementedError()
