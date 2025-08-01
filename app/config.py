import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class Config:
    """アプリケーション設定クラス"""
    
    # TikTok API設定
    TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
    TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
    STATE = "tokentest"
    
    # Flask設定
    SECRET_KEY = "tiktok_api_secret_key_2024"
    SESSION_COOKIE_SECURE = False  # ローカル開発用
    SESSION_COOKIE_HTTPONLY = False  # JavaScriptアクセスを許可
    SESSION_COOKIE_SAMESITE = 'Lax'  # SameSite設定
    PERMANENT_SESSION_LIFETIME = 300  # 5分間
    SESSION_COOKIE_DOMAIN = None  # ドメイン制限なし
    
    # TikTok API設定
    TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize"
    TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
    
    # アプリケーション設定
    DEBUG = True
    PORT = 3456 
