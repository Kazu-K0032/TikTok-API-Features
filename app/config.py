import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class Config:
    """アプリケーション設定クラス"""
    
    # TikTok API設定
    TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
    TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
    STATE = os.getenv("TIKTOK_STATE", "tokentest")
    
    # Flask設定
    SECRET_KEY = os.getenv("SECRET_KEY", "tiktok_api_secret_key_2024")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", "False").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    # 24時間セッション（86400秒）
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", "86400"))
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
    
    # TikTok API設定
    TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize"
    TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
    
    # アプリケーション設定
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", "3456"))
    
    # API設定
    DEFAULT_VIDEO_COUNT = int(os.getenv("DEFAULT_VIDEO_COUNT", "10"))
    MAX_VIDEO_COUNT = int(os.getenv("MAX_VIDEO_COUNT", "20"))
    
    # 複数ユーザー管理設定
    MAX_USERS_PER_SESSION = int(os.getenv("MAX_USERS_PER_SESSION", "5")) 
