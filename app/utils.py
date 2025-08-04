"""アプリケーション共通ユーティリティ"""

import logging
import os
from typing import Optional

def setup_logging() -> None:
    """ログ設定を初期化"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    console_output = os.getenv("CONSOLE_LOG", "false").lower() == "true"
    
    handlers = [logging.FileHandler('app.log', encoding='utf-8')]
    
    # 環境変数でターミナル出力を制御
    if console_output:
        handlers.append(logging.StreamHandler())
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # WerkzeugのINFOログを抑制
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得"""
    return logging.getLogger(name)

def validate_token(access_token: str) -> bool:
    """アクセストークンの基本的な検証"""
    if not access_token:
        return False
    
    # TikTok API v2のアクセストークン形式チェック
    # 実際のトークンは "act." で始まる
    if not access_token.startswith("act."):
        return False
    
    return True

def cleanup_caches() -> None:
    """キャッシュのクリーンアップを実行"""
    try:
        from app.services.cache import video_cache, profile_cache
        
        # 期限切れエントリを削除
        video_cleaned = video_cache.cleanup()
        profile_cleaned = profile_cache.cleanup()
        
        logger = get_logger(__name__)
        if video_cleaned > 0 or profile_cleaned > 0:
            logger.info(f"キャッシュクリーンアップ完了: 動画キャッシュ{video_cleaned}件, プロフィールキャッシュ{profile_cleaned}件を削除")
        
    except ImportError:
        # キャッシュモジュールが利用できない場合は何もしない
        pass 
