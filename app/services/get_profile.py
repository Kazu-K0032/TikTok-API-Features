import requests

def get_user_profile(access_token):
    # user.info.basic, user.info.profile, user.info.stats スコープで取得可能な情報
    # プロフィール情報と統計情報を一度に取得
    fields = "open_id,display_name,avatar_url,bio_description,profile_web_link,profile_deep_link,is_verified,follower_count,following_count,video_count,likes_count"
    
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
