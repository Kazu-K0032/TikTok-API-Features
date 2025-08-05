"""下書き投稿サービス"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DraftService:
    """下書き投稿管理サービス"""
    
    def __init__(self):
        self.drafts_dir = Path("drafts")
        self.drafts_dir.mkdir(exist_ok=True)
    
    def save_draft(self, user_open_id: str, draft_data: Dict[str, Any]) -> str:
        """下書きを保存"""
        try:
            # 下書きIDを生成（タイムスタンプベース）
            draft_id = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 下書きデータにメタデータを追加
            draft_data.update({
                'draft_id': draft_id,
                'user_open_id': user_open_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            # ファイルに保存
            draft_file = self.drafts_dir / f"{draft_id}.json"
            with open(draft_file, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"下書きを保存しました: {draft_id}")
            return draft_id
            
        except Exception as e:
            logger.error(f"下書き保存エラー: {e}")
            raise Exception("下書きの保存に失敗しました")
    
    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """下書きを取得"""
        try:
            draft_file = self.drafts_dir / f"{draft_id}.json"
            if not draft_file.exists():
                return None
            
            with open(draft_file, 'r', encoding='utf-8') as f:
                draft_data = json.load(f)
            
            return draft_data
            
        except Exception as e:
            logger.error(f"下書き取得エラー: {e}")
            return None
    
    def get_user_drafts(self, user_open_id: str) -> List[Dict[str, Any]]:
        """ユーザーの下書き一覧を取得"""
        try:
            drafts = []
            for draft_file in self.drafts_dir.glob("*.json"):
                try:
                    with open(draft_file, 'r', encoding='utf-8') as f:
                        draft_data = json.load(f)
                    
                    if draft_data.get('user_open_id') == user_open_id:
                        drafts.append(draft_data)
                except Exception as e:
                    logger.warning(f"下書きファイル読み込みエラー {draft_file}: {e}")
                    continue
            
            # 作成日時でソート（新しい順）
            drafts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return drafts
            
        except Exception as e:
            logger.error(f"下書き一覧取得エラー: {e}")
            return []
    
    def update_draft(self, draft_id: str, draft_data: Dict[str, Any]) -> bool:
        """下書きを更新"""
        try:
            draft_file = self.drafts_dir / f"{draft_id}.json"
            if not draft_file.exists():
                return False
            
            # 既存のデータを読み込み
            with open(draft_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # データを更新
            existing_data.update(draft_data)
            existing_data['updated_at'] = datetime.now().isoformat()
            
            # 保存
            with open(draft_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"下書きを更新しました: {draft_id}")
            return True
            
        except Exception as e:
            logger.error(f"下書き更新エラー: {e}")
            return False
    
    def delete_draft(self, draft_id: str) -> bool:
        """下書きを削除"""
        try:
            draft_file = self.drafts_dir / f"{draft_id}.json"
            if draft_file.exists():
                draft_file.unlink()
                logger.info(f"下書きを削除しました: {draft_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"下書き削除エラー: {e}")
            return False
    
    def get_draft_count(self, user_open_id: str) -> int:
        """ユーザーの下書き数を取得"""
        return len(self.get_user_drafts(user_open_id)) 
