import pytest
from datetime import datetime
from vsa.domain.models import MasterLead
from vsa.shared.enums import RecordStatus, LeadStage, SourceType
from vsa.infrastructure.converters import RowToModelConverter
from vsa.shared.constants import MasterLeadsColumns


class TestRowToModelConverter:
    """Row ↔ Model 変換のテスト"""

    def test_sheet_row_to_model_minimal(self):
        """最小限のデータでモデルに変換"""
        row = {
            MasterLeadsColumns.lead_id: "LEAD001",
            MasterLeadsColumns.record_status: "active",
            MasterLeadsColumns.lead_stage: "discovered_from_youtube",
            MasterLeadsColumns.canonical_company_name: "Example Corp",
        }
        
        model = RowToModelConverter.sheet_row_to_model(row)
        
        assert model.lead_id == "LEAD001"
        assert model.record_status == RecordStatus.ACTIVE
        assert model.lead_stage == LeadStage.DISCOVERED_FROM_YOUTUBE
        assert model.canonical_company_name == "Example Corp"

    def test_sheet_row_to_model_full(self):
        """全データでモデルに変換"""
        row = {
            MasterLeadsColumns.lead_id: "LEAD002",
            MasterLeadsColumns.record_status: "active",
            MasterLeadsColumns.lead_stage: "validated",
            MasterLeadsColumns.canonical_company_name: "Test Company",
            MasterLeadsColumns.official_url: "https://example.com",
            MasterLeadsColumns.official_domain: "example.com",
            MasterLeadsColumns.official_email: "contact@example.com",
            MasterLeadsColumns.phone_number: "09012345678",
            MasterLeadsColumns.ng_flag: "FALSE",
            MasterLeadsColumns.outreach_ready: "TRUE",
        }
        
        model = RowToModelConverter.sheet_row_to_model(row)
        
        assert model.lead_id == "LEAD002"
        assert model.official_url == "https://example.com"
        assert model.official_email == "contact@example.com"
        assert model.phone_number == "09012345678"
        assert model.ng_flag is False
        assert model.outreach_ready is True

    def test_model_to_sheet_row_minimal(self):
        """最小限のモデルをシート行に変換"""
        model = MasterLead(
            lead_id="LEAD003",
            record_status=RecordStatus.ACTIVE,
            lead_stage=LeadStage.DISCOVERED_FROM_YOUTUBE,
            canonical_company_name="Another Corp",
        )
        
        row = RowToModelConverter.model_to_sheet_row(model)
        
        assert row[MasterLeadsColumns.lead_id] == "LEAD003"
        assert row[MasterLeadsColumns.record_status] == "active"
        assert row[MasterLeadsColumns.lead_stage] == "discovered_from_youtube"
        assert row[MasterLeadsColumns.canonical_company_name] == "Another Corp"

    def test_model_to_sheet_row_full(self):
        """全データのモデルをシート行に変換"""
        model = MasterLead(
            lead_id="LEAD004",
            record_status=RecordStatus.ACTIVE,
            lead_stage=LeadStage.VALIDATED,
            canonical_company_name="Full Data Corp",
            official_url="https://fulldata.com",
            official_email="admin@fulldata.com",
            phone_number="09098765432",
            ng_flag=True,
            outreach_ready=False,
        )
        
        row = RowToModelConverter.model_to_sheet_row(model)
        
        assert row[MasterLeadsColumns.lead_id] == "LEAD004"
        assert row[MasterLeadsColumns.official_url] == "https://fulldata.com"
        assert row[MasterLeadsColumns.official_email] == "admin@fulldata.com"
        assert row[MasterLeadsColumns.ng_flag] == "TRUE"
        assert row[MasterLeadsColumns.outreach_ready] == "FALSE"

    def test_round_trip_conversion(self):
        """モデル -> シート行 -> モデル の往復変換"""
        original = MasterLead(
            lead_id="LEAD005",
            record_status=RecordStatus.ACTIVE,
            lead_stage=LeadStage.CONTACT_EXTRACTED,
            canonical_company_name="Round Trip Corp",
            official_domain="roundtrip.com",
            source_type=SourceType.OFFICIAL_SITE,
        )
        
        # モデル -> シート行
        row = RowToModelConverter.model_to_sheet_row(original)
        
        # シート行 -> モデル
        converted = RowToModelConverter.sheet_row_to_model(row)
        
        assert converted.lead_id == original.lead_id
        assert converted.canonical_company_name == original.canonical_company_name
        assert converted.official_domain == original.official_domain
        assert converted.source_type == original.source_type

    def test_bool_conversion(self):
        """Boolean 型の変換テスト"""
        # True -> "TRUE" -> True
        row_true = {
            MasterLeadsColumns.lead_id: "LEAD006",
            MasterLeadsColumns.record_status: "active",
            MasterLeadsColumns.lead_stage: "discovered_from_youtube",
            MasterLeadsColumns.canonical_company_name: "Bool Test",
            MasterLeadsColumns.ng_flag: "TRUE",
        }
        
        model = RowToModelConverter.sheet_row_to_model(row_true)
        assert model.ng_flag is True
        
        # False -> "FALSE" -> False
        row_false = row_true.copy()
        row_false[MasterLeadsColumns.ng_flag] = "FALSE"
        
        model = RowToModelConverter.sheet_row_to_model(row_false)
        assert model.ng_flag is False

    def test_datetime_conversion(self):
        """DateTime 型の変換テスト"""
        iso_date = "2026-05-07T14:45:00"
        
        row = {
            MasterLeadsColumns.lead_id: "LEAD007",
            MasterLeadsColumns.record_status: "active",
            MasterLeadsColumns.lead_stage: "discovered_from_youtube",
            MasterLeadsColumns.canonical_company_name: "DateTime Test",
            MasterLeadsColumns.created_at: iso_date,
        }
        
        model = RowToModelConverter.sheet_row_to_model(row)
        
        assert model.created_at is not None
        assert isinstance(model.created_at, datetime)
        assert model.created_at.year == 2026
        assert model.created_at.month == 5
        assert model.created_at.day == 7

    def test_enum_conversion(self):
        """Enum 型の変換テスト"""
        row = {
            MasterLeadsColumns.lead_id: "LEAD008",
            MasterLeadsColumns.record_status: "archived",
            MasterLeadsColumns.lead_stage: "validated",
            MasterLeadsColumns.canonical_company_name: "Enum Test",
            MasterLeadsColumns.source_type: "youtube",
        }
        
        model = RowToModelConverter.sheet_row_to_model(row)
        
        assert model.record_status == RecordStatus.ARCHIVED
        assert model.lead_stage == LeadStage.VALIDATED
        assert model.source_type == SourceType.YOUTUBE

    def test_missing_optional_fields(self):
        """オプショナルフィールドが欠落している場合"""
        row = {
            MasterLeadsColumns.lead_id: "LEAD009",
            MasterLeadsColumns.record_status: "active",
            MasterLeadsColumns.lead_stage: "discovered_from_youtube",
            MasterLeadsColumns.canonical_company_name: "Sparse Data",
        }
        
        model = RowToModelConverter.sheet_row_to_model(row)
        
        assert model.lead_id == "LEAD009"
        assert model.official_email is None
        assert model.phone_number is None
        assert model.ng_flag is False
