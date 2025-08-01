from flask import render_template, redirect, url_for, session, request
from app.auth_service import AuthService
from app.services.get_profile import get_user_profile
from app.services.get_video_list import get_video_list, format_create_time
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

        # プロフィール情報と統計情報を一度に取得
        profile = get_user_profile(token)
        print(f"Profile and stats data retrieved: {profile}")
        
        # 統計情報が含まれているかチェック
        stats_fields = ["follower_count", "following_count", "video_count", "likes_count"]
        missing_stats = [field for field in stats_fields if field not in profile or profile[field] is None]
        if missing_stats:
            print(f"Warning: Missing stats fields: {missing_stats}")
            # 不足している統計情報を0で初期化
            for field in missing_stats:
                profile[field] = 0
        
        print(f"Final profile data: {profile}")
        
        # 動画リストを取得
        videos = get_video_list(token, open_id, max_count=20)
        print(f"Retrieved videos: {len(videos)} videos")
        for i, video in enumerate(videos):
            print(f"Video {i+1}: {video.get('id')} - {video.get('title', 'No title')}")

        return render_template('dashboard.html', profile=profile, videos=videos)
    
    def video_detail(self, video_id):
        """動画詳細表示"""
        if "access_token" not in session:
            return redirect(url_for("index"))
        
        token = session["access_token"]
        details = get_video_details(token, video_id)
        
        print(f"Video detail data: {details}")
        
        # 画像URLの情報をログ出力
        if details:
            print(f"Available image URLs:")
            print(f"  - cover_image_url: {details.get('cover_image_url')}")
            print(f"  - best_image_url: {details.get('best_image_url')}")
        
        # 投稿日時をフォーマット
        if details.get("create_time"):
            details["formatted_create_time"] = format_create_time(details["create_time"])
        else:
            details["formatted_create_time"] = "不明"
        
        print(f"Formatted video detail data: {details}")
        
        return render_template('video_detail.html', d=details) 
