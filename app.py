import logging
from flask import Flask
# from flask_session import Session  # 標準のFlaskセッションを使用
from app.config import Config
from app.views import Views
from app.utils import setup_logging, cleanup_caches

def create_app():
    """Flaskアプリケーションを作成"""
    # ログ設定を初期化
    setup_logging()
    
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # 設定を適用
    config = Config()
    app.secret_key = config.SECRET_KEY
    # 標準のFlaskセッション設定
    app.config['PERMANENT_SESSION_LIFETIME'] = config.PERMANENT_SESSION_LIFETIME
    app.config['SESSION_COOKIE_SECURE'] = config.SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = config.SESSION_COOKIE_SAMESITE
    app.config['SESSION_COOKIE_DOMAIN'] = config.SESSION_COOKIE_DOMAIN
    
    # セッション設定をログに出力
    logger = logging.getLogger(__name__)
    logger.info(f"セッション設定: PERMANENT_SESSION_LIFETIME = {app.config.get('PERMANENT_SESSION_LIFETIME')}")
    logger.info(f"セッション設定: SESSION_COOKIE_SECURE = {app.config.get('SESSION_COOKIE_SECURE')}")
    logger.info(f"セッション設定: SESSION_COOKIE_HTTPONLY = {app.config.get('SESSION_COOKIE_HTTPONLY')}")
    logger.info(f"セッション設定: SESSION_COOKIE_SAMESITE = {app.config.get('SESSION_COOKIE_SAMESITE')}")
    
    # ビューコントローラーを初期化
    views = Views()
    
    # ルートを登録
    @app.route("/")
    def index():
        return views.index()
    
    @app.route("/login")
    def login():
        return views.login()
    
    @app.route("/callback/")
    def callback():
        return views.callback()
    
    @app.route("/dashboard")
    def dashboard():
        return views.dashboard()
    
    @app.route("/video/<video_id>")
    def video_detail(video_id):
        return views.video_detail(video_id)
    
    @app.route("/logout")
    def logout():
        return views.logout()
    
    # API エンドポイント
    @app.route("/api/switch-user", methods=["POST"])
    def api_switch_user():
        return views.api_switch_user()
    
    @app.route("/api/remove-user", methods=["POST"])
    def api_remove_user():
        return views.api_remove_user()
    
    @app.route("/api/user-data")
    def api_get_user_data():
        return views.api_get_user_data()
    
    @app.route("/api/users")
    def api_get_users():
        return views.api_get_users()
    
    @app.route("/debug/session")
    def debug_session():
        return views.debug_session()
    
    @app.route("/upload")
    def video_upload():
        return views.video_upload()
    
    @app.route("/api/upload-video", methods=["POST"])
    def api_upload_video():
        return views.api_upload_video()
    
    # 定期的なキャッシュクリーンアップ
    @app.before_request
    def before_request():
        # リクエストの10%でキャッシュクリーンアップを実行
        import random
        if random.random() < 0.1:
            cleanup_caches()
    
    return app

if __name__ == "__main__":
    # source venv/bin/activate
    # python app.py
    config = Config()
    app = create_app()
    app.run(debug=config.DEBUG, port=config.PORT) 
