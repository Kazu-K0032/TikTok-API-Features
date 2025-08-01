"""ユーザープロフィール情報取得サービス"""

from app.services.utils import make_tiktok_api_request, extract_user_data

def get_user_profile(access_token: str) -> dict:
    """ユーザープロフィール情報と統計情報を取得"""
    # user.info.basic, user.info.profile, user.info.stats スコープで取得可能な情報
    fields = "open_id,display_name,avatar_url,bio_description,profile_web_link,profile_deep_link,is_verified,follower_count,following_count,video_count,likes_count"
    
    response = make_tiktok_api_request(
        method="GET",
        url="https://open.tiktokapis.com/v2/user/info/",
        access_token=access_token,
        params={"fields": fields}
    )
    
    print(f"Profile API Response: {response}")
    
    user_data = extract_user_data(response)
    print(f"Extracted user data: {user_data}")
    
    return user_data
