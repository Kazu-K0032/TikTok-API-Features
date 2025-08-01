import requests

def get_video_details(access_token, video_id):
    """単一動画の詳細情報を取得"""
    try:
        # fieldsはURLクエリパラメータとして渡す
        fields = "id,title,duration,view_count,like_count,comment_count,share_count,embed_link,cover_image_url,height,width,created_time"
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
            return videos[0]  # 最初の動画を返す
        
        return {}
        
    except Exception as e:
        print(f"Video Detail API Exception: {e}")
        return {}
