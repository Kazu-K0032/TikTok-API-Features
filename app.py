from flask import Flask
from app.config import Config
from app.views import Views

def create_app():
    """Flaskアプリケーションを作成"""
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # 設定を適用
    config = Config()
    app.secret_key = config.SECRET_KEY
    app.config['SESSION_COOKIE_SECURE'] = config.SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = config.SESSION_COOKIE_SAMESITE
    app.config['PERMANENT_SESSION_LIFETIME'] = config.PERMANENT_SESSION_LIFETIME
    app.config['SESSION_COOKIE_DOMAIN'] = config.SESSION_COOKIE_DOMAIN
    
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
    
    return app

if __name__ == "__main__":
    # source venv/bin/activate
    # python app.py
    config = Config()
    app = create_app()
    app.run(debug=config.DEBUG, port=config.PORT) 
