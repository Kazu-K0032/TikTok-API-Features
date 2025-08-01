import requests

def get_best_image_url(video_data):
    """利用可能な画像URLを選択"""
    # 現在利用可能なフィールド: cover_image_url
    if video_data.get("cover_image_url"):
        return video_data["cover_image_url"]
    return None

def get_video_details(access_token, video_id):
    """単一動画の詳細情報を取得"""
    try:
        # fieldsはURLクエリパラメータとして渡す
        fields = "id,title,duration,view_count,like_count,comment_count,share_count,embed_link,cover_image_url,height,width,create_time"
        url = f"https://open.tiktokapis.com/v2/video/query/?fields={fields}"
        
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json={
                "filters": {
                    "video_ids": [video_id]
                }
            },
            timeout=10
        )
        
        if resp.status_code != 200:
            print(f"Video Detail API Error: {resp.status_code} - {resp.text}")
            print(f"Request JSON: {resp.request.body}")
            return {}
            
        json_data = resp.json()
        print(f"Video Detail API Response: {json_data}")
        
        videos = json_data.get("data", {}).get("videos", [])
        if videos:
            video_data = videos[0]  # 最初の動画を取得
            # 最適な画像URLを設定
            video_data["best_image_url"] = get_best_image_url(video_data)
            return video_data
        
        return {}
        
    except Exception as e:
        print(f"Video Detail API Exception: {e}")
        return {}
