from vsa.shared.enums import RecordStatus, LeadStage

def test_record_status():
    assert RecordStatus.ACTIVE.value == "active"
    assert RecordStatus.ARCHIVED.value == "archived"

def test_lead_stage():
    assert LeadStage.DISCOVERED_FROM_YOUTUBE.value == "discovered_from_youtube"
