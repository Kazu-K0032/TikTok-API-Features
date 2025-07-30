import requests

def get_video_details(access_token, video_id):
    resp = requests.get(
        "https://open.tiktokapis.com/v2/video/query/",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        params={
            "video_id": video_id,
            "fields": [
                "id","title","duration","view_count","like_count",
                "comment_count","share_count","embed_link","cover_image_url"
            ]
        }
    )
    return resp.json().get("data", {})
