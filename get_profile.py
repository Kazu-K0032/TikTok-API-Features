import requests

def get_user_profile(access_token):
    resp = requests.get(
        "https://open.tiktokapis.com/v2/user/info/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"fields": ["open_id","display_name","avatar_url","follower_count","following_count","likes_count","bio_description"]}
    )
    data = resp.json().get("data", {})
    return data  # user オブジェクトを返却
