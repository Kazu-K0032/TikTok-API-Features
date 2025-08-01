from flask import render_template, redirect, url_for, session, request
from app.auth_service import AuthService
from app.services.get_profile import get_user_profile
from app.services.get_user_stats import get_user_stats
from app.services.get_video_list import get_video_list
from app.services.get_video_details import get_video_details

class Views:
    """ビューコントローラー"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    def index(self):
        """ホームページ"""
        return render_template('index.html')
    
    def login(self):
        """ログイン処理開始"""
        auth_url = self.auth_service.start_auth()
        return redirect(auth_url)
    
    def callback(self):
        """認証コールバック処理"""
        code = request.args.get("code")
        state = request.args.get("state")
        
        result, error = self.auth_service.handle_callback(code, state)
        if error:
            return error, 400
        
        return redirect(url_for("dashboard"))
    
    def dashboard(self):
        """ダッシュボード表示"""
        if "access_token" not in session:
            return redirect(url_for("index"))
        
        token = session["access_token"]
        open_id = session.get("open_id")

        # プロフィール情報を取得
        profile = get_user_profile(token)
        
        # 統計情報を取得（user.info.statsスコープが必要）
        stats = get_user_stats(token, open_id)
        # プロフィール情報に統計情報をマージ
        profile.update(stats)
        print(f"Stats retrieved: {stats}")
        
        # 動画リストを取得
        videos = get_video_list(token, open_id, max_count=20)

        return render_template('dashboard.html', profile=profile, videos=videos)
    
    def video_detail(self, video_id):
        """動画詳細表示"""
        if "access_token" not in session:
            return redirect(url_for("index"))
        
        token = session["access_token"]
        details = get_video_details(token, video_id)
        
        return render_template('video_detail.html', d=details) 
