import hashlib
import string
import random
import requests
from flask import request, session
from app.config import Config

class AuthService:
    """TikTok認証サービス"""
    
    def __init__(self):
        self.config = Config()
        # メモリ内ストレージ（セッションの代替）
        self.session_data = {}
    
    def generate_pkce(self):
        """PKCE用のcode_verifierとcode_challengeを生成（TikTok公式仕様準拠）"""
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
    
    def get_redirect_uri(self):
        """動的にリダイレクトURIを生成（TikTokポータル設定と完全一致させる）"""
        # request.scheme と request.host を使い、常に実際のアクセス先と一致させる
        redirect_uri = f"{request.scheme}://{request.host}/callback/"
        print(f"Generated redirect URI: {redirect_uri}")
        return redirect_uri
    
    def start_auth(self):
        """認証プロセスを開始"""
        # 古いセッションデータをクリア
        session.clear()
        self.session_data.clear()  # メモリ保存もクリア
        
        uri = self.get_redirect_uri()
        
        # PKCEパラメータを生成
        code_verifier, code_challenge = self.generate_pkce()
        
        # セッションとメモリ内ストレージの両方に保存
        session.permanent = True
        session['code_verifier'] = code_verifier
        session.modified = True  # セッション変更を強制保存
        
        # メモリ内ストレージにも保存（メインストレージとして使用）
        self.session_data['code_verifier'] = code_verifier
        
        # 保存確認のデバッグ
        print(f"Login - Session code_verifier: {session.get('code_verifier', 'None')[:10]}...")
        print(f"Login - Memory code_verifier: {self.session_data.get('code_verifier', 'None')[:10]}...")
        
        # デバッグ情報を出力
        print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'N/A'}")
        print(f"Code Verifier saved: {code_verifier[:10]}...")
        print(f"Session contents: {dict(session)}")
        print(f"Memory storage: {self.session_data}")
        
        params = {
            "client_key": self.config.TIKTOK_CLIENT_KEY,
            "scope": "user.info.basic,user.info.stats,video.list",
            "response_type": "code",
            "redirect_uri": uri,
            "state": self.config.STATE,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        url = self.config.TIKTOK_AUTH_URL + "?" + "&".join(f"{k}={v}" for k,v in params.items())
        
        # デバッグ情報を出力
        print(f"Client Key: {self.config.TIKTOK_CLIENT_KEY}")
        print(f"Redirect URI: {uri}")
        print(f"Code Challenge: {code_challenge}")
        print(f"Auth URL: {url}")
        
        return url
    
    def handle_callback(self, code, state):
        """認証コールバックを処理"""
        # デバッグ情報を出力
        print(f"Callback - Session contents: {dict(session)}")
        print(f"Callback - Memory storage: {self.session_data}")
        print(f"Callback - Code: {code[:20] if code else 'None'}...")
        print(f"Callback - State: {state}")
        
        if state != self.config.STATE or not code:
            return None, "認証に失敗しました (Invalid state/code)"

        # メモリ保存されたcode_verifierを優先利用（セッションの不整合を回避）
        code_verifier = self.session_data.get('code_verifier')
        if not code_verifier:
            # フォールバック: セッションから取得
            code_verifier = session.get('code_verifier')
        
        print(f"Callback - Code Verifier: {code_verifier[:10] if code_verifier else 'None'}...")
        print(f"Callback - Code Verifier source: {'memory' if self.session_data.get('code_verifier') else 'session'}")
        
        if not code_verifier:
            return None, "認証に失敗しました (Missing code_verifier)"

        # Access Token の取得
        token_request_data = {
            "client_key": self.config.TIKTOK_CLIENT_KEY,
            "client_secret": self.config.TIKTOK_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.get_redirect_uri(),
            "code_verifier": code_verifier
        }
        
        print(f"Token Request Data: {token_request_data}")
        print(f"Token Request - Code Verifier: {code_verifier}")
        print(f"Token Request - Redirect URI: {self.get_redirect_uri()}")
        
        token_res = requests.post(
            self.config.TIKTOK_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=token_request_data
        )
        if token_res.status_code != 200:
            return None, f"Token Error: {token_res.text}"

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
            return None, f"Access token not found in response: {response_json}"
        
        if not access_token:
            return None, f"Access token is empty in response: {response_json}"

        # セッションに保存
        session["access_token"] = access_token
        session["open_id"] = open_id
        
        # code_verifierを削除（セキュリティのため）
        session.pop('code_verifier', None)

        return {"access_token": access_token, "open_id": open_id}, None 
