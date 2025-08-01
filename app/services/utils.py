"""TikTok API Services 共通ユーティリティ"""

import requests
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

def get_best_image_url(video_data: Dict[str, Any]) -> Optional[str]:
    """利用可能な画像URLを選択"""
    # 現在利用可能なフィールド: cover_image_url
    if video_data.get("cover_image_url"):
        return video_data["cover_image_url"]
    return None

def make_tiktok_api_request(
    method: str,
    url: str,
    access_token: str,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """TikTok API呼び出しの共通処理"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    if json_data:
        headers["Content-Type"] = "application/json"
    
    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method.upper() == "POST":
            resp = requests.post(url, headers=headers, params=params, json=json_data, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if resp.status_code != 200:
            logger.error(f"APIエラー: {resp.status_code} - {resp.text}")
            if json_data:
                logger.error(f"リクエストJSON: {json_data}")
            return {}
        
        return resp.json()
        
    except Exception as e:
        logger.error(f"API例外: {e}")
        return {}

def extract_user_data(response: Dict[str, Any]) -> Dict[str, Any]:
    """APIレスポンスからユーザーデータを抽出"""
    return response.get("data", {}).get("user", {})

def extract_videos_data(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """APIレスポンスから動画データを抽出"""
    return response.get("data", {}).get("videos", []) 
