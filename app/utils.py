"""アプリケーション共通ユーティリティ"""

import logging
import os
from typing import Optional

def setup_logging() -> None:
    """ログ設定を初期化"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )

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
