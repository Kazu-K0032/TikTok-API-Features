import hashlib
import string
import random
import requests
import logging
from flask import request, session
from app.config import Config

logger = logging.getLogger(__name__)

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
        logger.debug(f"PKCE Debug - Verifier length: {len(code_verifier)}")
        logger.debug(f"PKCE Debug - Challenge length: {len(code_challenge)}")
        logger.debug(f"PKCE Debug - Verifier: {code_verifier}")
        logger.debug(f"PKCE Debug - Challenge: {code_challenge}")
        logger.debug(f"PKCE Debug - Challenge is hex: {all(c in '0123456789abcdef' for c in code_challenge)}")
        
        # 検証用のデバッグ
        logger.debug(f"PKCE Debug - Verifier contains unreserved chars only: {all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~' for c in code_verifier)}")
        
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
        logger.debug(f"Login - Session code_verifier: {session.get('code_verifier', 'None')[:10]}...")
        logger.debug(f"Login - Memory code_verifier: {self.session_data.get('code_verifier', 'None')[:10]}...")
        
        # デバッグ情報を出力
        logger.debug(f"Session ID: {session.sid if hasattr(session, 'sid') else 'N/A'}")
        logger.debug(f"Code Verifier saved: {code_verifier[:10]}...")
        logger.debug(f"Session contents: {dict(session)}")
        logger.debug(f"Memory storage: {self.session_data}")
        
        params = {
            "client_key": self.config.TIKTOK_CLIENT_KEY,
            "scope": "user.info.basic,user.info.profile,user.info.stats,video.list",
            "response_type": "code",
            "redirect_uri": uri,
            "state": self.config.STATE,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        url = self.config.TIKTOK_AUTH_URL + "?" + "&".join(f"{k}={v}" for k,v in params.items())
        
        # デバッグ情報を出力
        logger.debug(f"Client Key: {self.config.TIKTOK_CLIENT_KEY}")
        logger.debug(f"Redirect URI: {uri}")
        logger.debug(f"Code Challenge: {code_challenge}")
        logger.debug(f"Auth URL: {url}")
        
        return url
    
    def handle_callback(self, code, state):
        """認証コールバックを処理"""
        # デバッグ情報を出力
        logger.debug(f"Callback - Session contents: {dict(session)}")
        logger.debug(f"Callback - Memory storage: {self.session_data}")
        logger.debug(f"Callback - Code: {code[:20] if code else 'None'}...")
        logger.debug(f"Callback - State: {state}")
        
        if state != self.config.STATE or not code:
            return None, "認証に失敗しました (Invalid state/code)"

        # メモリ保存されたcode_verifierを優先利用（セッションの不整合を回避）
        code_verifier = self.session_data.get('code_verifier')
        if not code_verifier:
            # フォールバック: セッションから取得
            code_verifier = session.get('code_verifier')
        
        logger.debug(f"Callback - Code Verifier: {code_verifier[:10] if code_verifier else 'None'}...")
        logger.debug(f"Callback - Code Verifier source: {'memory' if self.session_data.get('code_verifier') else 'session'}")
        
        if not code_verifier:
            logger.error("Missing code_verifier in callback")
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
        
        logger.debug(f"Token Request - Code Verifier: {code_verifier}")
        logger.debug(f"Token Request - Redirect URI: {self.get_redirect_uri()}")
        
        try:
            token_res = requests.post(
                self.config.TIKTOK_TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=token_request_data,
                timeout=30
            )
            
            logger.debug(f"Token Response Status: {token_res.status_code}")
            
            if token_res.status_code != 200:
                logger.error(f"Token Error: {token_res.status_code} - {token_res.text}")
                return None, f"Token Error: {token_res.text}"

            # レスポンスの詳細をデバッグ出力
            response_json = token_res.json()
            logger.debug(f"Token Response JSON: {response_json}")
            
            # TikTok v2の仕様に合わせて、ルート直下からアクセス
            if "access_token" in response_json:
                access_token = response_json["access_token"]
                open_id = response_json["open_id"]
                logger.info(f"Found access_token in root: {access_token[:20]}...")
            elif "data" in response_json:
                # 互換性のため、dataフィールドもサポート
                data = response_json["data"]
                access_token = data.get("access_token")
                open_id = data.get("open_id")
                logger.info(f"Found access_token in data field: {access_token[:20] if access_token else 'None'}...")
            else:
                logger.error(f"Access token not found in response: {response_json}")
                return None, f"Access token not found in response: {response_json}"
            
            if not access_token:
                logger.error(f"Access token is empty in response: {response_json}")
                return None, f"Access token is empty in response: {response_json}"

            # セッションに保存
            session["access_token"] = access_token
            session["open_id"] = open_id
            session.modified = True  # セッション変更を強制保存
            
            # code_verifierを削除（セキュリティのため）
            session.pop('code_verifier', None)
            
            logger.info(f"Authentication successful, session saved - Token: {access_token[:20]}..., Open ID: {open_id}")
            logger.debug(f"Session after save: {dict(session)}")
            return {"access_token": access_token, "open_id": open_id}, None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception during token exchange: {e}")
            return None, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {e}")
            return None, f"Unexpected error: {str(e)}" 
