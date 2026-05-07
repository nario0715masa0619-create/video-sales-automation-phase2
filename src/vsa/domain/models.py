from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from vsa.shared.enums import RecordStatus, LeadStage

@dataclass
class MasterLead:
    lead_id: str
    record_status: RecordStatus
    lead_stage: LeadStage
    canonical_company_name: str
    ng_flag: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def mark_updated(self) -> None:
        self.updated_at = datetime.now()
    
    def is_valid_for_outreach(self) -> bool:
        return self.record_status == RecordStatus.ACTIVE and not self.ng_flag
