"""動画一覧取得サービス"""

from datetime import datetime
from typing import List, Dict, Any
from app.services.utils import make_tiktok_api_request, extract_videos_data, get_best_image_url

def format_create_time(create_time):
    """投稿日時を読みやすい形式に変換"""
    if not create_time:
        return "不明"
    try:
        # UTC Unix epoch (seconds) を datetime に変換
        dt = datetime.fromtimestamp(create_time)
        return dt.strftime("%Y年%m月%d日 %H:%M")
    except:
        return "不明"

def get_video_details_batch(access_token: str, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """複数の動画の詳細情報を一括取得"""
    fields = "id,title,duration,view_count,like_count,comment_count,share_count,embed_link,cover_image_url,create_time"
    url = f"https://open.tiktokapis.com/v2/video/query/?fields={fields}"
    
    response = make_tiktok_api_request(
        method="POST",
        url=url,
        access_token=access_token,
        json_data={"filters": {"video_ids": video_ids}}
    )
    
    print(f"Video Query API Response: {response}")
    
    videos_data = extract_videos_data(response)
    
    # 動画IDをキーとした辞書に変換
    result = {}
    for video in videos_data:
        video_id = video.get("id")
        if video_id:
            result[video_id] = video
    
    print(f"Extracted detailed videos: {result}")
    return result

def get_video_list(access_token: str, open_id: str, max_count: int = 10) -> List[Dict[str, Any]]:
    """動画一覧を取得。video.listスコープが必要"""
    fields = "id,title,cover_image_url,create_time"
    url = f"https://open.tiktokapis.com/v2/video/list/?fields={fields}"
    
    response = make_tiktok_api_request(
        method="POST",
        url=url,
        access_token=access_token,
        json_data={"max_count": max_count}
    )
    
    print(f"Video List API Response: {response}")
    
    videos = extract_videos_data(response)
    print(f"Extracted videos: {videos}")
    
    # 動画IDのリストを取得して、詳細情報を一括取得
    if videos:
        video_ids = [video.get("id") for video in videos if video.get("id")]
        if video_ids:
            detailed_videos = get_video_details_batch(access_token, video_ids)
            # 基本情報と詳細情報をマージ
            for video in videos:
                video_id = video.get("id")
                if video_id and video_id in detailed_videos:
                    video.update(detailed_videos[video_id])
                
                # 最適な画像URLを設定
                video["best_image_url"] = get_best_image_url(video)
                
                # 投稿日時をフォーマット
                if video.get("create_time"):
                    video["formatted_create_time"] = format_create_time(video["create_time"])
                else:
                    video["formatted_create_time"] = "不明"
    
    return videos
