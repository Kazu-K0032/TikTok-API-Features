from flask import Flask, request, redirect, jsonify, render_template_string
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

app = Flask(__name__)
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")

# 環境に応じてリダイレクトURIを設定
def get_redirect_uri():
    # ローカル開発環境かどうかを判定
    if os.getenv("FLASK_ENV") == "development" or "localhost" in request.host_url:
        return "http://localhost:3456/callback"
    else:
        return "https://kazu-k0032.github.io/TikTok-API-Features/callback"

STATE = "tokentest"

# セッション管理用の簡易ストレージ（本番環境ではRedis等を使用）
session_data = {}

@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TikTok API Features</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .btn { background: #fe2c55; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
            .result { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .video-item { border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>TikTok API Features</h1>
            <p>TikTok APIを使用してアカウント認証、動画リスト、プロフィール情報、動画詳細を取得します。</p>
            <a href="/login" class="btn">TikTokでログイン</a>
        </div>
    </body>
    </html>
    """
    return html

@app.route("/login")
def login():
    redirect_uri = get_redirect_uri()
    # デバッグ情報を出力
    print(f"Client Key: {CLIENT_KEY}")
    print(f"Redirect URI: {redirect_uri}")
    
    params = {
        "client_key": CLIENT_KEY,
        "scope": "user.info.basic,video.list",
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "state": STATE
    }
    
    # URLパラメータを構築
    param_string = "&".join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"https://www.tiktok.com/v2/auth/authorize?{param_string}"
    
    print(f"Auth URL: {auth_url}")
    return redirect(auth_url)

@app.route("/callback/")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    if state != STATE or not code:
        return "Invalid state or missing code", 400

    # アクセストークンを取得
    redirect_uri = get_redirect_uri()
    token_resp = requests.post("https://open.tiktokapis.com/v2/oauth/token/", json={
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    })
    
    if token_resp.status_code != 200:
        return f"Token error: {token_resp.text}", 400
    
    data = token_resp.json().get("data", {})
    access_token = data.get("access_token")
    open_id = data.get("open_id")
    
    if not access_token:
        return f"Token error: {token_resp.text}", 400

    # セッションにトークンを保存
    session_data[open_id] = {
        "access_token": access_token,
        "open_id": open_id,
        "created_at": datetime.now().isoformat()
    }

    # プロフィール情報を取得
    profile_info = get_user_profile(access_token)
    
    # 動画リストを取得
    videos_info = get_video_list(access_token)
    
    # 結果を表示
    return render_results(profile_info, videos_info, open_id)

def get_user_profile(access_token):
    """ユーザープロフィール情報を取得"""
    try:
        resp = requests.get(
            "https://open.tiktokapis.com/v2/user/info/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            params={
                "fields": ["open_id", "union_id", "avatar_url", "avatar_url_100", "avatar_url_200", "display_name", "bio_description", "profile_deep_link", "is_verified", "follower_count", "following_count", "likes_count"]
            }
        )
        
        if resp.status_code == 200:
            return resp.json().get("data", {})
        else:
            return {"error": f"Profile fetch error: {resp.text}"}
    except Exception as e:
        return {"error": f"Profile fetch exception: {str(e)}"}

def get_video_list(access_token, max_count=10):
    """投稿動画のリストを取得"""
    try:
        resp = requests.post(
            "https://open.tiktokapis.com/v2/video/list/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={
                "max_count": max_count
            }
        )
        
        if resp.status_code == 200:
            return resp.json().get("data", {})
        else:
            return {"error": f"Video list fetch error: {resp.text}"}
    except Exception as e:
        return {"error": f"Video list fetch exception: {str(e)}"}

def get_video_details(access_token, video_id):
    """特定動画の詳細情報を取得"""
    try:
        resp = requests.get(
            "https://open.tiktokapis.com/v2/video/query/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            params={
                "fields": ["id", "title", "cover_image_url", "video_description", "duration", "height", "width", "share_url", "embed_html", "embed_link", "like_count", "comment_count", "share_count", "view_count", "created_time"],
                "video_id": video_id
            }
        )
        
        if resp.status_code == 200:
            return resp.json().get("data", {})
        else:
            return {"error": f"Video details fetch error: {resp.text}"}
    except Exception as e:
        return {"error": f"Video details fetch exception: {str(e)}"}

@app.route("/video/<video_id>")
def video_details(video_id):
    """特定動画の詳細情報を表示"""
    open_id = request.args.get("open_id")
    if not open_id or open_id not in session_data:
        return "Session not found. Please login again.", 400
    
    access_token = session_data[open_id]["access_token"]
    video_details = get_video_details(access_token, video_id)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Video Details - {video_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .btn {{ background: #fe2c55; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
            .result {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .video-detail {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>動画詳細情報</h1>
            <a href="/dashboard?open_id={open_id}" class="btn">ダッシュボードに戻る</a>
            <div class="video-detail">
                <h2>動画ID: {video_id}</h2>
                <pre>{video_details}</pre>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route("/dashboard")
def dashboard():
    """ダッシュボード表示"""
    open_id = request.args.get("open_id")
    if not open_id or open_id not in session_data:
        return redirect("/")
    
    access_token = session_data[open_id]["access_token"]
    
    # プロフィール情報を取得
    profile_info = get_user_profile(access_token)
    
    # 動画リストを取得
    videos_info = get_video_list(access_token)
    
    return render_results(profile_info, videos_info, open_id)

def render_results(profile_info, videos_info, open_id):
    """結果をHTMLで表示"""
    profile_html = ""
    if "error" not in profile_info:
        profile_html = f"""
        <div class="result">
            <h3>プロフィール情報</h3>
            <p><strong>表示名:</strong> {profile_info.get('display_name', 'N/A')}</p>
            <p><strong>フォロワー数:</strong> {profile_info.get('follower_count', 'N/A')}</p>
            <p><strong>フォロー数:</strong> {profile_info.get('following_count', 'N/A')}</p>
            <p><strong>いいね数:</strong> {profile_info.get('likes_count', 'N/A')}</p>
            <p><strong>自己紹介:</strong> {profile_info.get('bio_description', 'N/A')}</p>
        </div>
        """
    else:
        profile_html = f'<div class="result"><h3>プロフィール情報</h3><p>エラー: {profile_info["error"]}</p></div>'
    
    videos_html = ""
    if "error" not in videos_info:
        videos = videos_info.get("videos", [])
        if videos:
            videos_html = '<div class="result"><h3>投稿動画リスト</h3>'
            for video in videos:
                video_id = video.get("id", "")
                videos_html += f"""
                <div class="video-item">
                    <h4>動画ID: {video_id}</h4>
                    <p><strong>タイトル:</strong> {video.get('title', 'N/A')}</p>
                    <p><strong>再生時間:</strong> {video.get('duration', 'N/A')}秒</p>
                    <p><strong>いいね数:</strong> {video.get('like_count', 'N/A')}</p>
                    <p><strong>コメント数:</strong> {video.get('comment_count', 'N/A')}</p>
                    <p><strong>シェア数:</strong> {video.get('share_count', 'N/A')}</p>
                    <p><strong>再生数:</strong> {video.get('view_count', 'N/A')}</p>
                    <a href="/video/{video_id}?open_id={open_id}" class="btn">詳細を見る</a>
                </div>
                """
            videos_html += '</div>'
        else:
            videos_html = '<div class="result"><h3>投稿動画リスト</h3><p>動画が見つかりませんでした。</p></div>'
    else:
        videos_html = f'<div class="result"><h3>投稿動画リスト</h3><p>エラー: {videos_info["error"]}</p></div>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TikTok API Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .btn {{ background: #fe2c55; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
            .result {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .video-item {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>TikTok API Dashboard</h1>
            <a href="/" class="btn">ホームに戻る</a>
            {profile_html}
            {videos_html}
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(debug=True, port=3456)
