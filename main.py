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
from get_user_stats import get_user_stats
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
app.config['SESSION_COOKIE_DOMAIN'] = None  # ドメイン制限なし

# メモリ内ストレージ（セッションの代替）
session_data = {}

def generate_pkce():
    """PKCE用のcode_verifierとcode_challengeを生成（TikTok公式仕様準拠）"""
    import string
    import random
    
    # (1) code_verifier を 43文字以上のunreserved charsで生成
    chars = string.ascii_letters + string.digits + '-._~'
    code_verifier = ''.join(random.choice(chars) for _ in range(64))
    
    # (2) TikTok方式のchallengeはhex digest
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).hexdigest()
    
    # デバッグ情報
    print(f"PKCE Debug - Verifier length: {len(code_verifier)}")
    print(f"PKCE Debug - Challenge length: {len(code_challenge)}")
    print(f"PKCE Debug - Verifier: {code_verifier}")
    print(f"PKCE Debug - Challenge: {code_challenge}")
    print(f"PKCE Debug - Challenge is hex: {all(c in '0123456789abcdef' for c in code_challenge)}")
    
    # 検証用のデバッグ
    print(f"PKCE Debug - Verifier contains unreserved chars only: {all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~' for c in code_verifier)}")
    
    return code_verifier, code_challenge

def get_redirect_uri():
    """動的にリダイレクトURIを生成（TikTokポータル設定と完全一致させる）"""
    # request.scheme と request.host を使い、常に実際のアクセス先と一致させる
    redirect_uri = f"{request.scheme}://{request.host}/callback/"
    print(f"Generated redirect URI: {redirect_uri}")
    return redirect_uri

@app.route("/")
def index():
    return render_template_string("""
    <h1>TikTok API Dashboard</h1>
    <a href="{{ url_for('login') }}">▶ TikTok でログイン</a>
    """)

@app.route("/login")
def login():
    # 古いセッションデータをクリア
    session.clear()
    session_data.clear()  # メモリ保存もクリア
    
    uri = get_redirect_uri()
    
    # PKCEパラメータを生成
    code_verifier, code_challenge = generate_pkce()
    
    # セッションとメモリ内ストレージの両方に保存
    session.permanent = True
    session['code_verifier'] = code_verifier
    session.modified = True  # セッション変更を強制保存
    
    # メモリ内ストレージにも保存（メインストレージとして使用）
    session_data['code_verifier'] = code_verifier
    
    # 保存確認のデバッグ
    print(f"Login - Session code_verifier: {session.get('code_verifier', 'None')[:10]}...")
    print(f"Login - Memory code_verifier: {session_data.get('code_verifier', 'None')[:10]}...")
    
    # デバッグ情報を出力
    print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'N/A'}")
    print(f"Code Verifier saved: {code_verifier[:10]}...")
    print(f"Session contents: {dict(session)}")
    print(f"Memory storage: {session_data}")
    
    params = {
        "client_key":    CLIENT_KEY,
        "scope":         "user.info.basic,user.info.stats,video.list",
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

    # メモリ保存されたcode_verifierを優先利用（セッションの不整合を回避）
    code_verifier = session_data.get('code_verifier')
    if not code_verifier:
        # フォールバック: セッションから取得
        code_verifier = session.get('code_verifier')
    
    print(f"Callback - Code Verifier: {code_verifier[:10] if code_verifier else 'None'}...")
    print(f"Callback - Code Verifier source: {'memory' if session_data.get('code_verifier') else 'session'}")
    
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
    print(f"Token Request - Code Verifier: {code_verifier}")
    print(f"Token Request - Redirect URI: {get_redirect_uri()}")
    
    token_res = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=token_request_data
    )
    if token_res.status_code != 200:
        return f"Token Error: {token_res.text}", 400

    # レスポンスの詳細をデバッグ出力
    response_json = token_res.json()
    print(f"Token Response Status: {token_res.status_code}")
    print(f"Token Response JSON: {response_json}")
    
    # TikTok v2の仕様に合わせて、ルート直下からアクセス
    if "access_token" in response_json:
        access_token = response_json["access_token"]
        open_id = response_json["open_id"]
        print(f"Found access_token in root: {access_token[:20]}...")
    elif "data" in response_json:
        # 互換性のため、dataフィールドもサポート
        data = response_json["data"]
        access_token = data.get("access_token")
        open_id = data.get("open_id")
        print(f"Found access_token in data field: {access_token[:20] if access_token else 'None'}...")
    else:
        return f"Access token not found in response: {response_json}", 400
    
    if not access_token:
        return f"Access token is empty in response: {response_json}", 400

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
    open_id = session.get("open_id")

    # ── インポートした関数を利用 ──
    profile = get_user_profile(token)
    
    # 統計情報を取得（user.info.statsスコープが必要）
    try:
        stats = get_user_stats(token, open_id)
        # プロフィール情報に統計情報をマージ
        profile.update(stats)
        print(f"Stats successfully retrieved: {stats}")
    except Exception as e:
        print(f"Stats API Error: {e}")
        # 統計情報が取得できない場合はデフォルト値を設定
        profile.update({
            "follower_count": "N/A",
            "following_count": "N/A", 
            "video_count": "N/A",
            "likes_count": "N/A"
        })
        print("Using default N/A values for stats")
    
    videos = get_video_list(token, open_id, max_count=20)

    # 結果を表示
    return render_template_string("""
    <h1>プロフィール情報</h1>
    <ul>
      <li>表示名：{{ profile.display_name or '未設定' }}</li>
      <li>アバター：<img src="{{ profile.avatar_url or '' }}" alt="アバター" style="width:50px;height:50px;border-radius:50%;" onerror="this.style.display='none'"></li>
      <li>フォロワー数：{{ profile.follower_count }}</li>
      <li>フォロー数：{{ profile.following_count }}</li>
      <li>動画数：{{ profile.video_count }}</li>
      <li>いいね数：{{ profile.likes_count }}</li>
    </ul>
    <p><small>※ 統計情報（フォロワー数など）を取得するには user.info.stats スコープが必要です</small></p>

    <h1>投稿動画一覧</h1>
    {% for v in videos %}
      <div style="border:1px solid #ccc; padding:8px; margin-bottom:8px;">
        <div>
          <p><strong>ID:</strong> {{ v.id }} / <strong>タイトル:</strong> {{ v.title or 'タイトルなし' }}</p>
          <p><strong>再生時間:</strong> {{ v.duration }}秒 / <strong>再生数:</strong> {{ v.view_count }} / <strong>いいね:</strong> {{ v.like_count }}</p>
          <p><a href="{{ url_for('video_detail', video_id=v.id) }}">詳細を見る</a></p>
        </div>
      </div>
    {% else %}
      <p>動画が見つかりませんでした。</p>
      <p><small>※ 公開動画がないか、動画が存在しない可能性があります</small></p>
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
    <div style="display:flex; gap:20px;">
      <div style="flex:1;">
        <ul>
          <li><strong>ID:</strong> {{ d.id }}</li>
          <li><strong>タイトル:</strong> {{ d.title or 'タイトルなし' }}</li>
          <li><strong>再生時間:</strong> {{ d.duration }} 秒</li>
          <li><strong>再生数:</strong> {{ d.view_count }}</li>
          <li><strong>いいね数:</strong> {{ d.like_count }}</li>
          <li><strong>コメント数:</strong> {{ d.comment_count }}</li>
          <li><strong>シェア数:</strong> {{ d.share_count }}</li>
          {% if d.width and d.height %}
            <li><strong>解像度:</strong> {{ d.width }}×{{ d.height }}</li>
          {% endif %}
          {% if d.created_time %}
            <li><strong>投稿日時:</strong> {{ d.created_time }}</li>
          {% endif %}
        </ul>
        <p><a href="{{ d.embed_link }}" target="_blank">▶ 動画を開く</a></p>
        <p><a href="{{ url_for('dashboard') }}">← ダッシュボードへ戻る</a></p>
      </div>
      {% if d.cover_image_url %}
        <div style="flex:1;">
          <h3>サムネイル</h3>
          <img src="{{ d.cover_image_url }}" style="max-width:100%; height:auto;" alt="サムネイル">
        </div>
      {% endif %}
    </div>
    """, d=details)

if __name__ == "__main__":
    app.run(debug=True, port=3456)
