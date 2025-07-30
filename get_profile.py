import requests

def get_user_profile(access_token):
    # user.info.basic スコープで取得可能な基本情報のみ（確実に動作するフィールドのみ）
    fields = "open_id,display_name,avatar_url"
    
    resp = requests.get(
        "https://open.tiktokapis.com/v2/user/info/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"fields": fields}
    )
    json_data = resp.json()
    print(f"Profile API Response: {json_data}")
    
    # data.user の中身を直接返す
    user_data = json_data.get("data", {}).get("user", {})
    print(f"Extracted user data: {user_data}")
    return user_data
