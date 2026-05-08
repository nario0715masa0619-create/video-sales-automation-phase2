"""
Official Site Enrichment - Contact Extractor

HTML から電話番号、メールアドレス、問い合わせフォーム URL を抽出。
"""

from typing import Optional, List, Tuple
import re
import structlog

logger = structlog.get_logger(__name__)

class PhoneExtractor:
    """電話番号抽出"""
    
    # 日本の電話番号パターン
    PATTERNS = [
        r'\b0\d{1,4}-?\d{1,4}-?\d{4}\b',  # 0XX-XXXX-XXXX
        r'\b0\d{2,4}-?\d{1,4}-?\d{4}\b',  # 0XXX-XXX-XXXX
        r'\b0\d{10,11}\b',                 # 09012345678
    ]
    
    @staticmethod
    def extract(html: str) -> Optional[str]:
        """
        HTML から電話番号を抽出
        
        Args:
            html: HTML コンテンツ
            
        Returns:
            抽出された電話番号 または None
        """
        if not html:
            return None
        
        for pattern in PhoneExtractor.PATTERNS:
            matches = re.findall(pattern, html)
            if matches:
                # 最初の一致を返す
                phone = matches[0]
                # ハイフンを統一
                phone = phone.replace('-', '')
                return phone
        
        return None

class EmailExtractor:
    """メールアドレス抽出"""
    
    # メールアドレスパターン
    PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # 除外するメール (テスト用など)
    EXCLUDE_DOMAINS = ['test.com', 'example.com', 'sample.com']
    
    @staticmethod
    def extract(html: str) -> Optional[str]:
        """
        HTML からメールアドレスを抽出
        
        Args:
            html: HTML コンテンツ
            
        Returns:
            抽出されたメールアドレス または None
        """
        if not html:
            return None
        
        matches = re.findall(EmailExtractor.PATTERN, html)
        
        for email in matches:
            # 除外ドメインをチェック
            if not any(email.endswith(f"@{domain}") for domain in EmailExtractor.EXCLUDE_DOMAINS):
                return email
        
        return None

class ContactFormDetector:
    """問い合わせフォーム検出"""
    
    # 問い合わせフォームの指標
    FORM_INDICATORS = [
        r'<form[^>]*action=["\']?/contact',
        r'<form[^>]*id=["\']?contact',
        r'<form[^>]*name=["\']?contact',
        r'お問い合わせフォーム',
        r'問い合わせフォーム',
        r'contact-form',
        r'inquiry-form',
    ]
    
    @staticmethod
    def detect(html: str) -> Optional[str]:
        """
        HTML に問い合わせフォームが存在するか検出
        
        Args:
            html: HTML コンテンツ
            
        Returns:
            "found" または "not_found"
        """
        if not html:
            return None
        
        for indicator in ContactFormDetector.FORM_INDICATORS:
            if re.search(indicator, html, re.IGNORECASE):
                return "found"
        
        return "not_found"

class ContactExtractorOrchestrator:
    """連絡先抽出オーケストレーション"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
    
    def extract_all(self, html: str) -> Dict:
        """
        HTML からすべての連絡先情報を抽出
        
        Args:
            html: HTML コンテンツ
            
        Returns:
            {
              'phone_number': '...',
              'official_email': '...',
              'contact_form_status': 'found' | 'not_found',
            }
        """
        phone = PhoneExtractor.extract(html)
        email = EmailExtractor.extract(html)
        form_status = ContactFormDetector.detect(html)
        
        result = {
            'phone_number': phone,
            'official_email': email,
            'contact_form_status': form_status,
        }
        
        self.logger.info("Contact extraction completed",
                        phone=bool(phone), email=bool(email),
                        form_status=form_status)
        
        return result
