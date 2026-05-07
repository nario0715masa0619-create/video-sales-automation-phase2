from vsa.domain.models import MasterLead
from vsa.shared.enums import RecordStatus, LeadStage

def test_create_lead():
    lead = MasterLead(
        lead_id="LEAD001",
        record_status=RecordStatus.ACTIVE,
        lead_stage=LeadStage.DISCOVERED_FROM_YOUTUBE,
        canonical_company_name="Example Corp"
    )
    assert lead.lead_id == "LEAD001"
    assert lead.is_valid_for_outreach() is True

def test_ng_flag():
    lead = MasterLead(
        lead_id="LEAD002",
        record_status=RecordStatus.ACTIVE,
        lead_stage=LeadStage.VALIDATED,
        canonical_company_name="Example Corp",
        ng_flag=True
    )
    assert lead.is_valid_for_outreach() is False
