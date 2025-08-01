"""キャッシュ機能モジュール"""

import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Cache:
    """シンプルなメモリキャッシュクラス"""
    
    def __init__(self, ttl: int = 300):
        """
        キャッシュを初期化
        
        Args:
            ttl: キャッシュの有効期限（秒）
        """
        self.cache: Dict[str, Any] = {}
        self.ttl = ttl
        logger.debug(f"キャッシュを初期化 (TTL: {ttl}秒)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        キャッシュから値を取得
        
        Args:
            key: キャッシュキー
            
        Returns:
            キャッシュされた値、またはNone（期限切れまたは存在しない場合）
        """
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"キャッシュヒット: {key}")
                return data
            else:
                logger.debug(f"キャッシュ期限切れ: {key}")
                del self.cache[key]
        else:
            logger.debug(f"キャッシュミス: {key}")
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        キャッシュに値を保存
        
        Args:
            key: キャッシュキー
            value: 保存する値
        """
        self.cache[key] = (value, time.time())
        logger.debug(f"キャッシュに保存: {key}")
    
    def clear(self) -> None:
        """キャッシュをクリア"""
        self.cache.clear()
        logger.debug("キャッシュをクリア")
    
    def size(self) -> int:
        """キャッシュサイズを取得"""
        return len(self.cache)
    
    def cleanup(self) -> int:
        """
        期限切れのエントリを削除
        
        Returns:
            削除されたエントリ数
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"期限切れエントリを削除: {len(expired_keys)}個")
        
        return len(expired_keys)

# グローバルキャッシュインスタンス
video_cache = Cache(ttl=600)  # 動画データ: 10分
profile_cache = Cache(ttl=300)  # プロフィールデータ: 5分 
