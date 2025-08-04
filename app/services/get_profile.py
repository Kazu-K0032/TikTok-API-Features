"""ユーザープロフィール情報取得サービス"""

import logging
from typing import Dict, Any
from app.services.utils import make_tiktok_api_request, extract_user_data
from app.services.cache import profile_cache

logger = logging.getLogger(__name__)

def get_user_profile(access_token: str) -> Dict[str, Any]:
    """ユーザープロフィール情報と統計情報を取得"""
    # キャッシュキーを生成
    cache_key = f"profile_{access_token[:20]}"
    
    # キャッシュから取得を試行
    cached_data = profile_cache.get(cache_key)
    if cached_data:
        logger.info("プロフィールデータをキャッシュから取得")
        return cached_data
    
    # user.info.basic, user.info.profile, user.info.stats スコープで取得可能な情報
    fields = "open_id,display_name,username,avatar_url,bio_description,profile_web_link,profile_deep_link,is_verified,follower_count,following_count,video_count,likes_count"
    
    response = make_tiktok_api_request(
        method="GET",
        url="https://open.tiktokapis.com/v2/user/info/",
        access_token=access_token,
        params={"fields": fields}
    )
    
    logger.debug(f"プロフィールAPIレスポンス: {response}")
    
    user_data = extract_user_data(response)
    logger.debug(f"抽出されたユーザーデータ: {user_data}")
    
    # キャッシュに保存
    profile_cache.set(cache_key, user_data)
    
    return user_data
