"""
YouTube Discovery - API Client

YouTube API を使用してチャネル情報を取得するモジュール。
"""

from typing import Optional, Dict, List
import structlog

logger = structlog.get_logger(__name__)

class YouTubeAPIClient:
    """YouTube Data API v3 クライアント"""
    
    def __init__(self, api_key: str):
        """
        初期化
        
        Args:
            api_key: YouTube Data API キー
        """
        self.api_key = api_key
        self.logger = structlog.get_logger(__name__)
        
        # 実装ノート: youtube-api-python-client をインストール後、
        # googleapiclient.discovery.build を使用
        # from googleapiclient.discovery import build
        # self.service = build('youtube', 'v3', developerKey=api_key)
    
    def get_channel_by_url(self, channel_url: str) -> Optional[Dict]:
        """
        YouTube チャネル URL からチャネル情報を取得
        
        Args:
            channel_url: YouTube チャネル URL
                        (https://www.youtube.com/channel/UCxxxxx)
            
        Returns:
            {
              'channel_id': 'UCxxxxx',
              'channel_name': 'チャネル名',
              'description': 'チャネル説明',
              'subscriber_count': 1000,
              'view_count': 50000,
              'video_count': 100,
            }
        """
        if not channel_url:
            return None
        
        # チャネル ID を URL から抽出
        channel_id = self._extract_channel_id(channel_url)
        if not channel_id:
            return None
        
        return self.get_channel_by_id(channel_id)
    
    def get_channel_by_id(self, channel_id: str) -> Optional[Dict]:
        """
        チャネル ID からチャネル情報を取得
        
        Args:
            channel_id: YouTube チャネル ID
            
        Returns:
            チャネル情報 dict または None
        """
        if not channel_id:
            return None
        
        # TODO: YouTube API を実装
        # request = self.service.channels().list(
        #     part='snippet,statistics',
        #     id=channel_id
        # )
        # response = request.execute()
        # if response['items']:
        #     return self._parse_channel_response(response['items'][0])
        
        self.logger.info("Channel fetch (stub)", channel_id=channel_id)
        return None
    
    def get_channel_external_links(self, channel_id: str) -> List[str]:
        """
        チャネルの外部リンク (公式サイトなど) を取得
        
        Args:
            channel_id: YouTube チャネル ID
            
        Returns:
            外部リンク URL リスト
        """
        if not channel_id:
            return []
        
        # TODO: チャネルの説明やカスタムリンクから公式サイト URL を抽出
        # チャネル説明に含まれる URL を抽出
        # チャネルのカスタムリンク (Featured channels タブなど) を取得
        
        return []
    
    def _extract_channel_id(self, channel_url: str) -> Optional[str]:
        """
        YouTube チャネル URL からチャネル ID を抽出
        
        対応形式:
        - https://www.youtube.com/channel/UCxxxxx
        - https://youtube.com/c/channelname
        - https://youtube.com/@customurl
        
        Args:
            channel_url: チャネル URL
            
        Returns:
            チャネル ID または None
        """
        import re
        
        # 標準チャネル URL: /channel/UCxxxxx
        match = re.search(r'/channel/([a-zA-Z0-9_-]{24})', channel_url)
        if match:
            return match.group(1)
        
        # カスタム URL: /c/channelname または /@customurl
        # これらの場合は別途 lookup が必要
        match = re.search(r'(?:/c/|/@)([a-zA-Z0-9_-]+)', channel_url)
        if match:
            # TODO: カスタム URL からチャネル ID を lookup
            return None
        
        return None
    
    def _parse_channel_response(self, item: Dict) -> Dict:
        """
        YouTube API レスポンスをパース
        
        Args:
            item: API レスポンスアイテム
            
        Returns:
            パースされたチャネル情報
        """
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        
        return {
            'channel_id': item.get('id'),
            'channel_name': snippet.get('title'),
            'description': snippet.get('description'),
            'subscriber_count': int(statistics.get('subscriberCount', 0)),
            'view_count': int(statistics.get('viewCount', 0)),
            'video_count': int(statistics.get('videoCount', 0)),
        }
