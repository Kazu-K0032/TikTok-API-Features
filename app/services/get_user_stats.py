import requests

def get_user_stats(access_token, open_id):
    """ユーザーの統計情報を取得。user.info.statsスコープが必要"""
    # user.info.statsスコープで取得可能な統計情報
    fields = "follower_count,following_count,video_count,likes_count"
    
    try:
        resp = requests.get(
            "https://open.tiktokapis.com/v2/user/info/",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"fields": fields},
            timeout=5
        )
        
        # ステータスコードチェック
        if resp.status_code != 200 or not resp.text:
            raise ValueError(f"Invalid response: {resp.status_code}")

        json_data = resp.json()
        print(f"User Stats API Response: {json_data}")
        
        # data.user の中身を取得
        user_data = json_data.get("data", {}).get("user", {})
        print(f"Extracted stats data: {user_data}")

    except Exception as e:
        # ログ出力
        print(f"Stats API Error: {e}")
        user_data = {}

    # 統計情報を返す（数値が無ければデフォルト 0 を返す）
    return {
        "follower_count": user_data.get("follower_count", 0),
        "following_count": user_data.get("following_count", 0),
        "video_count": user_data.get("video_count", 0),
        "likes_count": user_data.get("likes_count", 0)
    } 
