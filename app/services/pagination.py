"""ページネーション機能モジュール"""

import math
from typing import List, Dict, Any, Optional

def paginate_videos(videos: List[Dict[str, Any]], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """
    動画リストをページネーション処理
    
    Args:
        videos: 動画リスト
        page: 現在のページ番号（1から開始）
        per_page: 1ページあたりの表示件数
        
    Returns:
        ページネーション情報を含む辞書
    """
    total = len(videos)
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    
    # ページ番号の検証
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
    
    # スライス範囲の計算
    start = (page - 1) * per_page
    end = start + per_page
    
    # 現在のページの動画を取得
    current_videos = videos[start:end]
    
    # ページネーション情報を構築
    pagination_info = {
        'videos': current_videos,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
        'start_index': start + 1 if total > 0 else 0,
        'end_index': min(end, total),
        'pages': _generate_page_numbers(page, total_pages)
    }
    
    return pagination_info

def _generate_page_numbers(current_page: int, total_pages: int, max_display: int = 5) -> List[int]:
    """
    表示するページ番号のリストを生成
    
    Args:
        current_page: 現在のページ
        total_pages: 総ページ数
        max_display: 最大表示ページ数
        
    Returns:
        表示するページ番号のリスト
    """
    if total_pages <= max_display:
        return list(range(1, total_pages + 1))
    
    # 現在のページを中心に表示
    half_display = max_display // 2
    start = max(1, current_page - half_display)
    end = min(total_pages, start + max_display - 1)
    
    # 開始位置を調整
    if end - start + 1 < max_display:
        start = max(1, end - max_display + 1)
    
    return list(range(start, end + 1))

def get_pagination_summary(pagination_info: Dict[str, Any]) -> str:
    """
    ページネーション情報のサマリー文字列を生成
    
    Args:
        pagination_info: ページネーション情報
        
    Returns:
        サマリー文字列
    """
    total = pagination_info['total']
    page = pagination_info['page']
    total_pages = pagination_info['total_pages']
    start_index = pagination_info['start_index']
    end_index = pagination_info['end_index']
    
    if total == 0:
        return "動画が見つかりません"
    
    return f"{total}件中 {start_index}-{end_index}件を表示 (ページ {page}/{total_pages})" 
