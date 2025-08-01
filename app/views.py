from flask import render_template, redirect, url_for, session, request
from app.auth_service import AuthService
from app.services.get_profile import get_user_profile
from app.services.get_video_list import get_video_list, format_create_time
from app.services.get_video_details import get_video_details
from app.utils import get_logger, validate_token

class Views:
    """ビューコントローラー"""
    
    def __init__(self):
        self.auth_service = AuthService()
        self.logger = get_logger(__name__)
    
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
        
        self.logger.info(f"Callback received - Code: {code[:20] if code else 'None'}..., State: {state}")
        
        if not code or not state:
            self.logger.error("Missing code or state in callback")
            return "認証に失敗しました (Missing parameters)", 400
        
        result, error = self.auth_service.handle_callback(code, state)
        if error:
            self.logger.error(f"Authentication failed: {error}")
            return error, 400
        
        self.logger.info("Authentication successful, redirecting to dashboard")
        return redirect(url_for("dashboard"))
    
    def dashboard(self):
        """ダッシュボード表示"""
        self.logger.info("Dashboard access attempt")
        self.logger.debug(f"Dashboard access - Session contents: {dict(session)}")
        
        if "access_token" not in session:
            self.logger.warning("Access token not found in session")
            return redirect(url_for("index"))
        
        token = session["access_token"]
        open_id = session.get("open_id")
        
        self.logger.info(f"Dashboard - Token found: {token[:20] if token else 'None'}..., Open ID: {open_id}")
        
        # トークンの有効性チェック
        if not validate_token(token):
            self.logger.warning(f"Invalid access token format: {token[:20] if token else 'None'}...")
            session.clear()
            return redirect(url_for("index"))
        
        self.logger.info("Token validation successful")

        try:
            # プロフィール情報と統計情報を一度に取得
            profile = get_user_profile(token)
            self.logger.info("Profile and stats data retrieved successfully")
            
            # 統計情報が含まれているかチェック
            stats_fields = ["follower_count", "following_count", "video_count", "likes_count"]
            missing_stats = [field for field in stats_fields if field not in profile or profile[field] is None]
            if missing_stats:
                self.logger.warning(f"Missing stats fields: {missing_stats}")
                # 不足している統計情報を0で初期化
                for field in missing_stats:
                    profile[field] = 0
            
            # 動画リストを取得
            videos = get_video_list(token, open_id, max_count=20)
            self.logger.info(f"Retrieved {len(videos)} videos")
            
            return render_template('dashboard.html', profile=profile, videos=videos)
            
        except Exception as e:
            self.logger.error(f"Error in dashboard: {str(e)}")
            return "エラーが発生しました", 500
    
    def video_detail(self, video_id):
        """動画詳細表示"""
        if "access_token" not in session:
            self.logger.warning("Access token not found in session for video detail")
            return redirect(url_for("index"))
        
        token = session["access_token"]
        
        # トークンの有効性チェック
        if not validate_token(token):
            self.logger.warning("Invalid access token format for video detail")
            session.clear()
            return redirect(url_for("index"))
        
        try:
            details = get_video_details(token, video_id)
            self.logger.info(f"Video detail retrieved for video_id: {video_id}")
            
            # 投稿日時をフォーマット
            if details.get("create_time"):
                details["formatted_create_time"] = format_create_time(details["create_time"])
            else:
                details["formatted_create_time"] = "不明"
            
            return render_template('video_detail.html', d=details)
            
        except Exception as e:
            self.logger.error(f"Error in video_detail for video_id {video_id}: {str(e)}")
            return "エラーが発生しました", 500 
