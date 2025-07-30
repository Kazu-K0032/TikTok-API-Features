import requests

def get_user_stats(access_token, open_id):
    """ユーザーの統計情報を取得"""
    resp = requests.get(
        "https://open.tiktokapis.com/v2/user/stats/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"open_id": open_id}
    )
    json_data = resp.json()
    print(f"User Stats API Response: {json_data}")
    
    data = json_data.get("data", {})
    return {
        "follower_count": data.get("follower_count", 0),
        "following_count": data.get("following_count", 0),
        "video_count": data.get("video_count", 0),
        "likes_count": data.get("likes_count", 0)
    } 
