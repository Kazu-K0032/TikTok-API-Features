import requests

def get_video_details_batch(access_token, video_ids):
    """複数の動画の詳細情報を一括取得"""
    try:
        # fieldsはURLクエリパラメータとして渡す
        fields = "id,title,duration,view_count,like_count,comment_count,share_count,embed_link,cover_image_url,height,width,created_time"
        url = f"https://open.tiktokapis.com/v2/video/query/?fields={fields}"
        
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json={
                "filters": {
                    "video_ids": video_ids
                }
            },
            timeout=10
        )
        
        if resp.status_code != 200:
            print(f"Video Query API Error: {resp.status_code} - {resp.text}")
            print(f"Request JSON: {resp.request.body}")
            return {}
            
        json_data = resp.json()
        print(f"Video Query API Response: {json_data}")
        
        videos_data = json_data.get("data", {}).get("videos", [])
        
        # 動画IDをキーとした辞書に変換
        result = {}
        for video in videos_data:
            video_id = video.get("id")
            if video_id:
                result[video_id] = video
        
        print(f"Extracted detailed videos: {result}")
        return result
        
    except Exception as e:
        print(f"Video Query API Exception: {e}")
        return {}

def get_video_list(access_token, open_id, max_count=10):
    """動画一覧を取得。video.listスコープが必要"""
    try:
        # fieldsはURLクエリパラメータとして渡す
        fields = "id,title,duration,cover_image_url,embed_link"
        url = f"https://open.tiktokapis.com/v2/video/list/?fields={fields}"
        
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json={
                "max_count": max_count
            },
            timeout=10
        )
        
        if resp.status_code != 200:
            print(f"Video List API Error: {resp.status_code} - {resp.text}")
            print(f"Request JSON: {resp.request.body}")
            return []
            
        json_data = resp.json()
        print(f"Video List API Response: {json_data}")
        
        videos = json_data.get("data", {}).get("videos", [])
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
        
        return videos
        
    except Exception as e:
        print(f"Video List API Exception: {e}")
        return []
