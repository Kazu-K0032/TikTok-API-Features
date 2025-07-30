import requests

def get_video_list(access_token, open_id, max_count=10):
    resp = requests.post(
        "https://open.tiktokapis.com/v2/video/list/",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={
            "open_id": open_id,
            "cursor": 0,
            "count": max_count,
            "fields": [
                "id","title","duration","view_count",
                "like_count","comment_count","share_count","embed_link"
            ]
        }
    )
    json_data = resp.json()
    print(f"Video List API Response: {json_data}")
    
    videos = json_data.get("data", {}).get("videos", [])
    print(f"Extracted videos: {videos}")
    return videos
