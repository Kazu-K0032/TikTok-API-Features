import requests

def get_video_list(access_token, max_count=10):
    resp = requests.post(
        "https://open.tiktokapis.com/v2/video/list/",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={"max_count": max_count}
    )
    return resp.json().get("data", {}).get("videos", [])
