"""動画詳細情報取得サービス"""

import logging
from typing import Dict, Any
from app.services.utils import make_tiktok_api_request, extract_videos_data, get_best_image_url
from app.services.cache import video_cache

logger = logging.getLogger(__name__)

def get_video_details(access_token: str, video_id: str) -> Dict[str, Any]:
    """単一動画の詳細情報を取得"""
    # キャッシュキーを生成
    cache_key = f"video_detail_{video_id}"
    
    # キャッシュから取得を試行
    cached_data = video_cache.get(cache_key)
    if cached_data:
        logger.info(f"動画詳細データをキャッシュから取得: {video_id}")
        return cached_data
    
    fields = "id,title,duration,view_count,like_count,comment_count,share_count,embed_link,cover_image_url,height,width,create_time"
    url = f"https://open.tiktokapis.com/v2/video/query/?fields={fields}"
    
    response = make_tiktok_api_request(
        method="POST",
        url=url,
        access_token=access_token,
        json_data={"filters": {"video_ids": [video_id]}}
    )
    
    logger.debug(f"動画詳細APIレスポンス: {response}")
    
    videos = extract_videos_data(response)
    if videos:
        video_data = videos[0]  # 最初の動画を取得
        # 最適な画像URLを設定
        video_data["best_image_url"] = get_best_image_url(video_data)
        
        # キャッシュに保存
        video_cache.set(cache_key, video_data)
        
        return video_data
    
    return {}
