from flask import Flask, request, redirect, render_template_string, session, url_for
import requests
import os
import base64
import hashlib
import secrets
from datetime import datetime
from dotenv import load_dotenv

# 外部モジュールから関数をインポート
from get_profile import get_user_profile
from get_video_list import get_video_list
from get_video_details import get_video_details

# 環境変数を読み込み
load_dotenv()

CLIENT_KEY    = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
STATE         = "tokentest"

app = Flask(__name__)
app.secret_key = "tiktok_api_secret_key_2024"  # 固定のセッションキー
app.config['SESSION_COOKIE_SECURE'] = False  # ローカル開発用
app.config['SESSION_COOKIE_HTTPONLY'] = False  # JavaScriptアクセスを許可
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # SameSite設定
app.config['PERMANENT_SESSION_LIFETIME'] = 300  # 5分間

# メモリ内ストレージ（セッションの代替）
session_data = {}

def generate_pkce():
    """PKCE用のcode_verifierとcode_challengeを生成"""
    # 32バイトのランダムデータを生成
    code_verifier_bytes = secrets.token_bytes(32)
    
    # Base64URLエンコーディング（パディングなし）
    code_verifier = base64.urlsafe_b64encode(code_verifier_bytes).decode('utf-8').rstrip('=')
    
    # SHA256ハッシュを計算
    code_challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    
    # Base64URLエンコーディング（パディングなし）
    code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('utf-8').rstrip('=')
    
    # デバッグ情報
    print(f"PKCE Debug - Verifier length: {len(code_verifier)}")
    print(f"PKCE Debug - Challenge length: {len(code_challenge)}")
    print(f"PKCE Debug - Verifier: {code_verifier}")
    print(f"PKCE Debug - Challenge: {code_challenge}")
    
    return code_verifier, code_challenge

def get_redirect_uri():
    """開発環境なら localhost, 本番は GitHub Pages を返す"""
    host = request.host_url
    # localhost または 127.0.0.1 のいずれかを検出
    if os.getenv("FLASK_ENV")=="development" or "localhost" in host or "127.0.0.1" in host:
        # 一時的にGitHub Pagesを使用してテスト
        print("Using GitHub Pages redirect URI for testing")
        return "https://kazu-k0032.github.io/TikTok-API-Features/callback/"
    return "https://kazu-k0032.github.io/TikTok-API-Features/callback/"

@app.route("/")
def index():
    return render_template_string("""
    <h1>TikTok API Dashboard</h1>
    <a href="{{ url_for('login') }}">▶ TikTok でログイン</a>
    """)

@app.route("/login")
def login():
    uri = get_redirect_uri()
    
    # PKCEパラメータを生成
    code_verifier, code_challenge = generate_pkce()
    
    # セッションとメモリ内ストレージの両方に保存
    session.permanent = True
    session['code_verifier'] = code_verifier
    session.modified = True  # セッション変更を強制保存
    
    # メモリ内ストレージにも保存（バックアップ）
    session_data['code_verifier'] = code_verifier
    
    # デバッグ情報を出力
    print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'N/A'}")
    print(f"Code Verifier saved: {code_verifier[:10]}...")
    print(f"Session contents: {dict(session)}")
    print(f"Memory storage: {session_data}")
    
    params = {
        "client_key":    CLIENT_KEY,
        "scope":         "user.info.basic,video.list",
        "response_type": "code",
        "redirect_uri":  uri,
        "state":         STATE,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    url = "https://www.tiktok.com/v2/auth/authorize?" + "&".join(f"{k}={v}" for k,v in params.items())
    
    # デバッグ情報を出力
    print(f"Client Key: {CLIENT_KEY}")
    print(f"Redirect URI: {uri}")
    print(f"Code Challenge: {code_challenge}")
    print(f"Auth URL: {url}")
    
    return redirect(url)

@app.route("/callback/")
def callback():
    code  = request.args.get("code")
    state = request.args.get("state")
    
    # デバッグ情報を出力
    print(f"Callback - Session contents: {dict(session)}")
    print(f"Callback - Memory storage: {session_data}")
    print(f"Callback - Code: {code[:20] if code else 'None'}...")
    print(f"Callback - State: {state}")
    
    if state != STATE or not code:
        return "認証に失敗しました (Invalid state/code)", 400

    # セッションからcode_verifierを取得（メモリ内ストレージをバックアップとして使用）
    code_verifier = session.get('code_verifier')
    if not code_verifier:
        code_verifier = session_data.get('code_verifier')
    
    print(f"Callback - Code Verifier: {code_verifier[:10] if code_verifier else 'None'}...")
    
    if not code_verifier:
        return "認証に失敗しました (Missing code_verifier)", 400

    # Access Token の取得
    token_request_data = {
        "client_key":    CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "grant_type":    "authorization_code",
        "code":          code,
        "redirect_uri":  get_redirect_uri(),
        "code_verifier": code_verifier
    }
    
    print(f"Token Request Data: {token_request_data}")
    
    token_res = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=token_request_data,  # jsonではなくdataを使用
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if token_res.status_code != 200:
        return f"Token Error: {token_res.text}", 400

    # レスポンスの詳細をデバッグ出力
    response_json = token_res.json()
    print(f"Token Response Status: {token_res.status_code}")
    print(f"Token Response JSON: {response_json}")
    
    data = response_json.get("data", {})
    print(f"Data field: {data}")
    
    # 安全にアクセストークンを取得
    access_token = data.get("access_token")
    open_id = data.get("open_id")
    
    if not access_token:
        return f"Access token not found in response: {response_json}", 400

    # セッションに保存
    session["access_token"] = access_token
    session["open_id"]      = open_id
    
    # code_verifierを削除（セキュリティのため）
    session.pop('code_verifier', None)

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if "access_token" not in session:
        return redirect(url_for("index"))
    token = session["access_token"]

    # ── インポートした関数を利用 ──
    profile = get_user_profile(token)
    videos  = get_video_list(token, max_count=20)

    # 結果を表示
    return render_template_string("""
    <h1>プロフィール情報</h1>
    <ul>
      <li>表示名：{{ profile.display_name }}</li>
      <li>フォロワー：{{ profile.follower_count }}</li>
      <li>フォロー：{{ profile.following_count }}</li>
      <li>いいね：{{ profile.likes_count }}</li>
      <li>自己紹介：{{ profile.bio_description }}</li>
    </ul>

    <h1>投稿動画一覧</h1>
    {% for v in videos %}
      <div style="border:1px solid #ccc; padding:8px; margin-bottom:8px;">
        <p>ID: {{ v.id }} / タイトル: {{ v.title }}</p>
        <p><a href="{{ url_for('video_detail', video_id=v.id) }}">詳細を見る</a></p>
      </div>
    {% else %}
      <p>動画が見つかりませんでした。</p>
    {% endfor %}

    <p><a href="{{ url_for('index') }}">← ホームへ戻る</a></p>
    """, profile=profile, videos=videos)

@app.route("/video/<video_id>")
def video_detail(video_id):
    if "access_token" not in session:
        return redirect(url_for("index"))
    token = session["access_token"]

    # ── インポートした関数を利用 ──
    details = get_video_details(token, video_id)

    return render_template_string("""
    <h1>動画詳細情報</h1>
    <ul>
      <li>ID: {{ d.id }}</li>
      <li>タイトル: {{ d.title }}</li>
      <li>再生時間: {{ d.duration }} 秒</li>
      <li>再生数: {{ d.view_count }}</li>
      <li>いいね数: {{ d.like_count }}</li>
      <li>コメント数: {{ d.comment_count }}</li>
      <li>シェア数: {{ d.share_count }}</li>
    </ul>
    <p><a href="{{ d.embed_link }}" target="_blank">▶ 動画を開く</a></p>
    <p><a href="{{ url_for('dashboard') }}">← ダッシュボードへ戻る</a></p>
    """, d=details)

if __name__ == "__main__":
    app.run(debug=True, port=3456)
