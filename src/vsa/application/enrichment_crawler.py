"""
Official Site Enrichment - Crawler

公式サイトから HTML を取得するモジュール。
"""

from typing import Optional, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import structlog

logger = structlog.get_logger(__name__)

class OfficialSiteCrawler:
    """公式サイトをクロール"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        初期化
        
        Args:
            timeout: リクエストタイムアウト (秒)
            max_retries: リトライ回数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
        self.logger = structlog.get_logger(__name__)
    
    def _create_session(self) -> requests.Session:
        """
        リトライロジック付きセッションを作成
        
        Returns:
            requests.Session
        """
        session = requests.Session()
        
        retry = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # User-Agent を設定（ロボットブロック対策）
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        return session
    
    def crawl(self, url: str) -> Optional[str]:
        """
        URL をクロール
        
        Args:
            url: クロール対象 URL
            
        Returns:
            HTML コンテンツ または None
        """
        if not url:
            return None
        
        try:
            self.logger.info("Crawling URL", url=url)
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self.logger.info("Crawl success", url=url, status=response.status_code)
            
            return response.text
            
        except requests.exceptions.Timeout:
            self.logger.warning("Crawl timeout", url=url, timeout=self.timeout)
            return None
        except requests.exceptions.ConnectionError:
            self.logger.warning("Crawl connection error", url=url)
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.warning("Crawl HTTP error", url=url, status=e.response.status_code)
            return None
        except Exception as e:
            self.logger.error("Crawl failed", url=url, error=str(e))
            return None
    
    def close(self):
        """セッションをクローズ"""
        self.session.close()
