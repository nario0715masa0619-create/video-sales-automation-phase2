"""
Validation & Contactability - Orchestrator

メール/電話検証と到達可能性判定パイプラインを統合するモジュール。
"""

from typing import Optional, Dict
from datetime import datetime
import structlog

from vsa.domain.models import MasterLead
from vsa.shared.enums import (
    EmailValidationStatus, MailSendable, ContactFormSendable,
    OutreachChannel, ContactabilityStatus, OutreachBlockReason,
    RecordStatus, SalesStatus
)

logger = structlog.get_logger(__name__)

class ValidationOrchestrator:
    """検証パイプライン全体を統合"""
    
    def __init__(self, zerobounce_api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            zerobounce_api_key: ZeroBounce API キー
        """
        self.zerobounce_api_key = zerobounce_api_key
        self.logger = structlog.get_logger(__name__)
    
    def validate_lead(self, lead: MasterLead) -> MasterLead:
        """
        リード全体を検証
        
        Args:
            lead: MasterLead
            
        Returns:
            検証済み MasterLead
        """
        # メール検証
        if lead.official_email:
            self._validate_email(lead)
        
        # 電話番号検証
        if lead.phone_number:
            self._validate_phone(lead)
        
        # 到達可能性判定
        self._compute_contactability(lead)
        
        # アウトリーチ準備状態判定
        self._compute_outreach_readiness(lead)
        
        lead.mark_updated()
        
        self.logger.info("Lead validation completed", lead_id=lead.lead_id,
                        email_status=lead.email_validation_status,
                        contactability=lead.contactability_status,
                        outreach_ready=lead.outreach_ready)
        
        return lead
    
    def _validate_email(self, lead: MasterLead) -> None:
        """
        メールアドレスを検証
        
        Args:
            lead: MasterLead (修正される)
        """
        email = lead.official_email
        
        # TODO: ZeroBounce API を実装
        # response = requests.get(
        #     'https://api.zerobounce.net/v2/validate',
        #     params={
        #         'api_key': self.zerobounce_api_key,
        #         'email': email
        #     }
        # )
        # result = response.json()
        # lead.email_validation_status = EmailValidationStatus(result['status'])
        # lead.email_validation_score = result.get('score', 0)
        # lead.email_validation_provider = 'zerobounce'
        # lead.email_validation_at = datetime.now()
        
        # スタブ: メール形式チェック
        if '@' in email and '.' in email:
            lead.email_validation_status = EmailValidationStatus.VALID
            lead.email_sendable = MailSendable.TRUE
        else:
            lead.email_validation_status = EmailValidationStatus.INVALID
            lead.email_sendable = MailSendable.FALSE
        
        lead.email_validation_at = datetime.now()
    
    def _validate_phone(self, lead: MasterLead) -> None:
        """
        電話番号を検証
        
        Args:
            lead: MasterLead (修正される)
        """
        phone = lead.phone_number
        
        # 日本の電話番号形式チェック
        import re
        
        # ハイフンを除去
        clean_phone = phone.replace('-', '')
        
        # 日本の電話番号パターン
        if re.match(r'^0\d{9,10}$', clean_phone):
            # 有効な形式
            lead.phone_confidence = 'high'  # TODO: Enum を使用
        else:
            # 無効な形式
            pass
    
    def _compute_contactability(self, lead: MasterLead) -> None:
        """
        到達可能性を判定
        
        Args:
            lead: MasterLead (修正される)
        """
        # 到達可能な連絡先が最低1つあるか
        has_email = (lead.official_email and 
                    lead.email_validation_status == EmailValidationStatus.VALID)
        has_phone = bool(lead.phone_number)
        has_form = lead.contact_form_status and lead.contact_form_status.value == 'found'
        
        if has_email or has_phone or has_form:
            lead.contactability_status = ContactabilityStatus.REACHABLE
        else:
            lead.contactability_status = ContactabilityStatus.UNREACHABLE
        
        # 好適なチャネルを決定
        if has_email:
            lead.preferred_outreach_channel = OutreachChannel.EMAIL
        elif has_form:
            lead.preferred_outreach_channel = OutreachChannel.FORM
        elif has_phone:
            lead.preferred_outreach_channel = OutreachChannel.EMAIL  # デフォルト
        else:
            lead.preferred_outreach_channel = OutreachChannel.NONE
    
    def _compute_outreach_readiness(self, lead: MasterLead) -> None:
        """
        アウトリーチ準備状態を判定
        
        到達可能性、NG フラグ、営業状態、レコード状態を総合判定
        
        Args:
            lead: MasterLead (修正される)
        """
        # チェック項目
        checks = {
            'record_status': lead.record_status == RecordStatus.ACTIVE,
            'ng_flag': not lead.ng_flag,
            'sales_status': lead.sales_status not in (SalesStatus.WON, SalesStatus.LOST, SalesStatus.NG),
            'contactability': lead.contactability_status != ContactabilityStatus.UNREACHABLE,
            'contact_info': bool(lead.official_email or lead.phone_number),
        }
        
        # すべてのチェックをパス
        if all(checks.values()):
            lead.outreach_ready = True
            lead.outreach_block_reason = OutreachBlockReason.NONE
        else:
            lead.outreach_ready = False
            
            # ブロック理由を特定
            if not checks['record_status']:
                lead.outreach_block_reason = OutreachBlockReason.NOT_OUTREACH_READY
            elif not checks['ng_flag']:
                lead.outreach_block_reason = OutreachBlockReason.NG_FLAG
            elif not checks['sales_status']:
                lead.outreach_block_reason = OutreachBlockReason.SALES_STATUS_BLOCKED
            elif not checks['contactability']:
                lead.outreach_block_reason = OutreachBlockReason.NO_VALID_CONTACT
            else:
                lead.outreach_block_reason = OutreachBlockReason.NONE
    
    def validate_batch(self, leads: list) -> list:
        """
        リードバッチを検証
        
        Args:
            leads: MasterLead リスト
            
        Returns:
            検証済み MasterLead リスト
        """
        validated = []
        
        for i, lead in enumerate(leads):
            try:
                validated_lead = self.validate_lead(lead)
                validated.append(validated_lead)
            except Exception as e:
                self.logger.error("Validation failed", lead_id=lead.lead_id, error=str(e))
                validated.append(lead)
            
            if (i + 1) % 50 == 0:
                self.logger.info("Progress", validated=i + 1, total=len(leads))
        
        self.logger.info("Batch validation completed", total=len(leads))
        
        return validated
