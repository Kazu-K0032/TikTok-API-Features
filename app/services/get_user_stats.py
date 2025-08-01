import requests

def get_user_stats(access_token, open_id):
    """ユーザーの統計情報を取得。失敗時でも 0 を返す"""
    url = "https://open.tiktokapis.com/v2/user/stats/"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"open_id": open_id}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        # ステータスコードチェック
        if resp.status_code != 200 or not resp.text:
            raise ValueError(f"Invalid response: {resp.status_code}")

        json_data = resp.json()
        print(f"User Stats API Response: {json_data}")
        data = json_data.get("data", {})

    except Exception as e:
        # ログ出力（必要なら）
        print(f"Stats API Error: {e}")
        data = {}

    # data 内に数字が無ければデフォルト 0 を返す
    return {
        "follower_count": data.get("follower_count", 0),
        "following_count": data.get("following_count", 0),
        "video_count": data.get("video_count", 0),
        "likes_count": data.get("likes_count", 0)
    } 
