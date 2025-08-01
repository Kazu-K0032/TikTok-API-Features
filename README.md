# TikTok API Features

TikTok API を使用してユーザープロフィール情報と投稿動画を取得・表示する Flask アプリケーションです。

## 機能

- TikTok OAuth 2.0 認証（PKCE 方式）
- ユーザープロフィール情報の取得・表示
- 統計情報（フォロワー数、フォロー数、いいね数、動画数）の表示
- 投稿動画一覧の取得・表示
- 動画詳細情報の表示
- レスポンシブデザイン対応

## 技術スタック

- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **API**: TikTok API v2
- **認証**: OAuth 2.0 with PKCE
- **ログ**: Python logging

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`env.example`を参考に`.env`ファイルを作成してください：

```bash
cp env.example .env
```

必要な環境変数：

- `TIKTOK_CLIENT_KEY`: TikTok Developer Portal で取得した Client Key
- `TIKTOK_CLIENT_SECRET`: TikTok Developer Portal で取得した Client Secret
- `SECRET_KEY`: Flask アプリケーションの秘密鍵

### 3. TikTok Developer Portal 設定

1. [TikTok Developer Portal](https://developers.tiktok.com/)でアプリケーションを作成
2. 必要なスコープを有効化：
   - `user.info.basic`
   - `user.info.profile`
   - `user.info.stats`
   - `video.list`
3. リダイレクト URI を設定：`http://localhost:3456/callback/`

### 4. アプリケーションの起動

```bash
python app.py
```

アプリケーションは `http://localhost:3456` で起動します。

## アーキテクチャ

```
app/
├── __init__.py
├── config.py          # アプリケーション設定
├── auth_service.py    # TikTok認証サービス
├── views.py          # ビューコントローラー
├── utils.py          # 共通ユーティリティ
└── services/         # APIサービス層
    ├── __init__.py
    ├── utils.py      # API共通ユーティリティ
    ├── get_profile.py
    ├── get_video_list.py
    └── get_video_details.py

static/
├── css/
│   ├── base.css
│   ├── dashboard.css
│   ├── video-detail.css
│   └── responsive.css
└── js/

templates/
├── base.html
├── index.html
├── dashboard.html
└── video_detail.html
```

## 改善点

### セキュリティ強化

- 環境変数による設定管理
- トークン有効性チェック
- セッション管理の改善

### エラーハンドリング

- 構造化ログシステムの導入
- 例外処理の強化
- ユーザーフレンドリーなエラーメッセージ

### コード品質

- 型ヒントの統一
- 責務分離の徹底
- 共通ユーティリティの活用

## ログ

アプリケーションは以下のログファイルを生成します：

- `app.log`: アプリケーションログ

ログレベルは環境変数 `LOG_LEVEL` で制御可能です（DEBUG, INFO, WARNING, ERROR）。

## ライセンス

MIT License
