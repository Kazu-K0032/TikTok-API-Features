"""動画アップロードサービス"""

import logging
import requests
import os
from typing import Dict, Any, Optional, Tuple
from app.services.utils import make_tiktok_api_request

logger = logging.getLogger(__name__)

def get_creator_info(access_token: str) -> Dict[str, Any]:
    """投稿先クリエイター情報を取得（最新情報を常に取得）"""
    url = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
    
    try:
        # 最新情報を常に取得するため、キャッシュヘッダーを追加
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        response = requests.post(
            url,
            headers=headers,
            json={},
            timeout=30
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # レスポンスの妥当性を検証
        if 'data' not in response_data:
            logger.error("クリエイター情報レスポンスに'data'フィールドがありません")
            raise Exception("クリエイター情報のレスポンス形式が不正です")
        
        # TikTok APIの仕様に従って、dataフィールドが直接クリエイター情報を含む場合がある
        if 'creator_info' in response_data['data']:
            return response_data
        elif 'creator_avatar_url' in response_data['data']:
            # dataフィールドが直接クリエイター情報を含む場合
            return response_data
        else:
            logger.error("クリエイター情報レスポンスに'creator_info'またはクリエイター情報フィールドがありません")
            raise Exception("クリエイター情報のレスポンス形式が不正です")
        
        return response
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logger.error("クリエイター情報取得エラー: 認証エラー - Content Posting APIの権限が不足しています")
            raise Exception("Content Posting APIの権限が不足しています。アプリの設定でContent Posting APIを有効にしてください。")
        elif e.response.status_code == 429:
            logger.error("クリエイター情報取得エラー: レート制限に達しました（20リクエスト/分）")
            raise Exception("APIレート制限に達しました。しばらく時間をおいてから再試行してください。")
        else:
            logger.error(f"クリエイター情報取得エラー: HTTP {e.response.status_code} - {e.response.text}")
            raise
    except requests.exceptions.Timeout as e:
        logger.error(f"クリエイター情報取得エラー: タイムアウト - {e}")
        raise Exception("クリエイター情報の取得がタイムアウトしました。しばらく時間をおいてから再試行してください。")
    except Exception as e:
        logger.error(f"クリエイター情報取得エラー: {e}")
        raise

def initialize_video_upload(
    access_token: str,
    title: str,
    video_size: int,
    privacy_level: str = "SELF_ONLY",  # 未監査クライアントはSELF_ONLYのみ対応
    disable_comment: bool = False,
    disable_duet: bool = False,
    disable_stitch: bool = False,
    is_draft: bool = False  # 下書き投稿かどうか
) -> Dict[str, Any]:
    """動画投稿リクエストを初期化"""
    if is_draft:
        url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
        logger.info("下書き投稿モードで動画アップロードを初期化")
    else:
        url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        logger.info("直接投稿モードで動画アップロードを初期化")
    
    # TikTok APIの推奨チャンクサイズ（10MB = 10,000,000 bytes）
    # ただし、動画サイズが推奨チャンクサイズより小さい場合は動画サイズをチャンクサイズとする
    recommended_chunk_size = 10 * 1024 * 1024  # 10MB
    
    # 動画サイズが0の場合はチャンクサイズも0とする（エラーハンドリングのため）
    if video_size == 0:
        chunk_size = 0
        total_chunk_count = 0
    else:
        # 動画サイズが推奨チャンクサイズより小さい場合は、動画サイズをチャンクサイズとする
        chunk_size = min(video_size, recommended_chunk_size)
        # チャンク数が0になるのを防ぐため、動画サイズが0でなければ最低1チャンクとする
        total_chunk_count = (video_size + chunk_size - 1) // chunk_size if chunk_size > 0 else 1

    logger.info(f"動画サイズ: {video_size} bytes, チャンクサイズ: {chunk_size} bytes, チャンク数: {total_chunk_count}")
    
    request_data = {
        "post_info": {
            "title": title,
            "privacy_level": privacy_level,
            "disable_comment": disable_comment,
            "disable_duet": disable_duet,
            "disable_stitch": disable_stitch,
            "video_cover_timestamp_ms": 1000  # 1秒目をカバー画像として使用
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunk_count
        }
    }
    
    try:
        response = make_tiktok_api_request(
            method="POST",
            url=url,
            access_token=access_token,
            json_data=request_data
        )
        
        logger.info(f"動画アップロード初期化成功: レスポンス全体={response}")
        if 'data' in response:
            logger.info(f"初期化データ: {response['data']}")
        if 'error' in response:
            logger.info(f"初期化エラー情報: {response['error']}")
        return response
        
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.text
        logger.error(f"動画アップロード初期化エラー: HTTP {e.response.status_code} - {error_detail}")
        
        if e.response.status_code == 400:
            raise Exception(f"動画アップロード初期化エラー: {error_detail}")
        elif e.response.status_code == 403:
            if "unaudited_client_can_only_post_to_private_accounts" in error_detail:
                raise Exception("未監査クライアントはプライベートアカウントのみに投稿できます。TikTokアプリでアカウントをプライベート設定に変更してください。")
            else:
                raise Exception(f"動画アップロード初期化エラー: {error_detail}")
        elif e.response.status_code == 429:
            raise Exception("APIレート制限に達しました。しばらく時間をおいてから再試行してください。")
        else:
            raise Exception(f"動画アップロード初期化エラー: HTTP {e.response.status_code} - {error_detail}")
    except Exception as e:
        logger.error(f"動画アップロード初期化エラー: {e}")
        raise

def upload_video_chunk(upload_url: str, video_data: bytes, content_range: str) -> bool:
    """動画データをチャンクでアップロード"""
    headers = {
        "Content-Range": content_range,
        "Content-Length": str(len(video_data)),
        "Content-Type": "video/mp4"
    }
    
    try:
        response = requests.put(
            upload_url,
            headers=headers,
            data=video_data,
            timeout=60
        )
        
        # TikTok APIでは201 Createdが成功を示す
        if response.status_code in [200, 201]:
            logger.info(f"動画チャンクアップロード成功: {response.status_code} - {content_range}")
            return True
        else:
            logger.error(f"動画チャンクアップロード失敗: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"動画チャンクアップロードエラー: {e}")
        return False

def upload_video_file_chunked(upload_url: str, video_file_path: str) -> bool:
    """動画ファイルをチャンクでアップロード（公式ドキュメント準拠）"""
    try:
        file_size = os.path.getsize(video_file_path)
        
        # initialize_video_uploadと同じチャンクサイズ計算ロジックを使用
        recommended_chunk_size = 10 * 1024 * 1024  # 10MB
        if file_size == 0:
            chunk_size = 0
        else:
            chunk_size = min(file_size, recommended_chunk_size)
        
        if chunk_size == 0 and file_size > 0: # For very small files that might result in 0 chunk_size if min(0, recommended)
            chunk_size = file_size # Ensure chunk_size is at least file_size if file_size is small.
        elif chunk_size == 0 and file_size == 0:
            logger.warning("動画ファイルサイズが0のため、アップロードをスキップします。")
            return True # Nothing to upload

        total_chunk_count = (file_size + chunk_size - 1) // chunk_size if chunk_size > 0 else 0
        if total_chunk_count == 0 and file_size > 0:
            total_chunk_count = 1 # At least one chunk for a non-empty video

        with open(video_file_path, 'rb') as f:
            for chunk_index in range(total_chunk_count):
                start_byte = chunk_index * chunk_size
                end_byte = min(start_byte + chunk_size - 1, file_size - 1)
                
                # チャンクデータを読み込み
                f.seek(start_byte)
                chunk_data = f.read(end_byte - start_byte + 1)
                
                # Content-Rangeヘッダーを作成
                content_range = f"bytes {start_byte}-{end_byte}/{file_size}"
                
                # チャンクをアップロード
                if not upload_video_chunk(upload_url, chunk_data, content_range):
                    logger.error(f"チャンク {chunk_index + 1} のアップロードに失敗")
                    return False
        
        return True
    except Exception as e:
        logger.error(f"動画ファイルチャンクアップロードエラー: {e}")
        return False

def upload_video_file(upload_url: str, video_file_path: str) -> bool:
    """動画ファイルをアップロード"""
    try:
        file_size = os.path.getsize(video_file_path)
        
        with open(video_file_path, 'rb') as f:
            video_data = f.read()
        
        content_range = f"bytes 0-{file_size-1}/{file_size}"
        
        return upload_video_chunk(upload_url, video_data, content_range)
        
    except Exception as e:
        logger.error(f"動画ファイルアップロードエラー: {e}")
        return False

def get_post_status(access_token: str, publish_id: str) -> Dict[str, Any]:
    """投稿ステータスを取得"""
    url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
    
    request_data = {
        "publish_id": publish_id
    }
    
    try:
        response = make_tiktok_api_request(
            method="POST",
            url=url,
            access_token=access_token,
            json_data=request_data
        )
        
        logger.info(f"投稿ステータス取得成功: {response.get('status')}")
        return response
        
    except Exception as e:
        logger.error(f"投稿ステータス取得エラー: {e}")
        raise

def upload_video_complete(
    access_token: str,
    video_file_path: str,
    title: str,
    privacy_level: str = "SELF_ONLY",  # 未監査クライアントはSELF_ONLYのみ対応
    disable_comment: bool = False,
    disable_duet: bool = False,
    disable_stitch: bool = False,
    is_draft: bool = False  # 下書き投稿かどうか
) -> Tuple[bool, str, Optional[str]]:
    """動画アップロードの完全なプロセスを実行"""
    upload_type = "下書き投稿" if is_draft else "直接投稿"
    
    try:
        # 1. クリエイター情報を取得（最新情報を常に取得）
        creator_info = get_creator_info(access_token)
        
        # アカウントのプライバシー設定を確認
        if 'data' in creator_info:
            # TikTok APIの仕様に従って、dataフィールドが直接クリエイター情報を含む場合がある
            if 'creator_info' in creator_info['data']:
                creator_info_data = creator_info['data']['creator_info']
            elif 'creator_avatar_url' in creator_info['data']:
                # dataフィールドが直接クリエイター情報を含む場合
                creator_info_data = creator_info['data']
            else:
                logger.warning("クリエイター情報の形式が不正です")
                creator_info_data = {}
            if 'privacy_level_options' in creator_info_data:
                # 正しいプライベートアカウント判定
                is_private_account = 'PUBLIC_TO_EVERYONE' not in creator_info_data['privacy_level_options'] and 'FOLLOWER_OF_CREATOR' in creator_info_data['privacy_level_options']
                
                if not is_private_account:
                    error_msg = "アカウントがプライベート設定ではありません。TikTokアプリで「設定」→「プライバシー」→「アカウント」を「プライベート」に変更してください。"
                    logger.error(error_msg)
                    return False, error_msg, None
        
        # 2. 動画ファイルサイズを取得
        video_size = os.path.getsize(video_file_path)
        
        # 3. アップロードを初期化
        init_response = initialize_video_upload(
            access_token=access_token,
            title=title,
            video_size=video_size,
            privacy_level=privacy_level,
            disable_comment=disable_comment,
            disable_duet=disable_duet,
            disable_stitch=disable_stitch,
            is_draft=is_draft
        )
        
        # TikTok APIのレスポンス形式に従って、dataフィールドから取得
        if 'data' in init_response:
            publish_id = init_response['data'].get('publish_id')
            upload_url = init_response['data'].get('upload_url')
        else:
            publish_id = init_response.get('publish_id')
            upload_url = init_response.get('upload_url')
        
        if not publish_id or not upload_url:
            logger.error(f"{upload_type}: アップロード初期化に失敗: publish_id={publish_id}, upload_url={upload_url}")
            return False, "アップロード初期化に失敗しました", None
        
        # 4. 動画ファイルをチャンクでアップロード（公式ドキュメント準拠）
        upload_success = upload_video_file_chunked(upload_url, video_file_path)
        
        if not upload_success:
            logger.error(f"{upload_type}: 動画ファイルのアップロードに失敗しました")
            return False, "動画ファイルのアップロードに失敗しました", publish_id
        
        # 5. 投稿ステータスを確認（非同期処理のため少し待機）
        import time
        time.sleep(3)  # TikTok APIの非同期処理を待つ
        
        try:
            status_response = get_post_status(access_token, publish_id)
        except Exception as e:
            logger.warning(f"{upload_type}: 投稿ステータス取得エラー（アップロードは成功）: {e}")
        
        # 動画リンクとプロフィールリンクを生成
        username = creator_info_data.get('creator_username', '')
        
        # publish_idから動画IDを抽出
        # 例: v_pub_file~v2-1.7534632449491552261 → 7534632449491552261
        # 例: v_pub_file~v2-1.7534635204204546104 → 7534635204204546104
        if '~' in publish_id:
            # ~の後の部分を取得
            parts = publish_id.split('~')
            if len(parts) > 1:
                # 最後の部分から数字を抽出
                last_part = parts[-1]
                # 数字のみを抽出（ドットやその他の文字を除去）
                import re
                numbers = re.findall(r'\d+', last_part)
                if numbers:
                    video_id = numbers[-1]  # 最後の数字を使用
                else:
                    video_id = last_part
            else:
                video_id = publish_id
        else:
            video_id = publish_id
        
        profile_link = f"https://www.tiktok.com/@{username}"
        
        if is_draft:
            success_message = f"動画をTikTokの下書きに保存しました。\nTikTokアプリの通知を確認して、動画を編集・投稿してください。\nプロフィール: {profile_link}"
        else:
            success_message = f"動画アップロードが完了しました。\nプロフィール: {profile_link}"
        
        return True, success_message, publish_id
        
    except Exception as e:
        logger.error(f"動画アップロードプロセスエラー: {e}")
        return False, f"アップロードエラー: {str(e)}", None 
