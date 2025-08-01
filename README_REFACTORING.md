# リファクタリング後の構造

## 責務分離の実装

元の`main.py`から以下の責務を分離しました：

### 1. 設定管理 (`app/config.py`)

- 環境変数の読み込み
- Flask 設定
- TikTok API 設定
- アプリケーション設定

### 2. 認証サービス (`app/auth_service.py`)

- OAuth 認証ロジック
- PKCE 生成
- トークン管理
- セッション管理

### 3. ビューコントローラー (`app/views.py`)

- ビジネスロジック
- データ取得
- テンプレート選択

### 4. API サービス (`app/services/`)

- `get_profile.py`: プロフィール情報取得
- `get_user_stats.py`: ユーザー統計情報取得
- `get_video_list.py`: 動画リスト取得
- `get_video_details.py`: 動画詳細情報取得

### 5. テンプレート (`templates/`)

- `base.html`: 共通レイアウト
- `index.html`: ホームページ
- `dashboard.html`: ダッシュボード
- `video_detail.html`: 動画詳細

### 6. 静的ファイル (`static/`)

- `css/style.css`: スタイルシート
- `js/`: JavaScript ファイル（将来の拡張用）

### 7. アプリケーション (`app.py`)

- Flask アプリケーション作成
- ルーティング設定
- 依存性注入

## 新しいファイル構造

```
tiktok-api-features/
├── app.py                    # メインアプリケーション
├── app/                      # アプリケーションパッケージ
│   ├── __init__.py
│   ├── config.py             # 設定管理
│   ├── auth_service.py       # 認証サービス
│   ├── views.py              # ビューコントローラー
│   └── services/             # API サービス
│       ├── __init__.py
│       ├── get_profile.py
│       ├── get_user_stats.py
│       ├── get_video_list.py
│       └── get_video_details.py
├── templates/                # テンプレート
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── video_detail.html
├── static/                   # 静的ファイル
│   ├── css/
│   │   └── style.css
│   └── js/
├── requirements.txt
├── README.md
├── README_REFACTORING.md     # このファイル
└── .gitignore
```

## 責務分離のメリット

### 1. 保守性の向上

- 各ファイルが単一の責務を持つ
- 変更時の影響範囲が限定される
- コードの理解が容易

### 2. テスタビリティの向上

- 各コンポーネントを独立してテスト可能
- モックやスタブの作成が容易

### 3. 再利用性の向上

- 認証サービスを他のプロジェクトで再利用可能
- 設定管理を他の Flask アプリで再利用可能
- API サービスを他のアプリケーションで再利用可能

### 4. 拡張性の向上

- 新しい機能の追加が容易
- 既存機能の修正が他に影響しない
- 静的ファイルの管理が改善

## 使用方法

### 開発環境での実行

```bash
python app.py
```

### 本番環境での実行

```bash
export FLASK_APP=app.py
export FLASK_ENV=production
flask run
```

## 今後の改善点

1. **データベース層の追加**

   - SQLAlchemy を使用したデータ永続化
   - ユーザー情報のキャッシュ

2. **エラーハンドリングの強化**

   - カスタム例外クラス
   - エラーページのテンプレート

3. **ログ機能の追加**

   - 構造化ログ
   - ログレベル管理

4. **テストの追加**

   - ユニットテスト
   - 統合テスト

5. **API 層の分離**

   - RESTful API エンドポイント
   - JSON レスポンス

6. **フロントエンドの改善**
   - JavaScript の追加
   - レスポンシブデザインの強化

## 移行手順

1. 新しいファイル構造を作成
2. 既存のファイルを適切なディレクトリに移動
3. インポートパスを更新
4. 静的ファイルを分離
5. 動作確認
6. 不要なファイルを削除

この構造により、コードの保守性、テスタビリティ、再利用性が大幅に向上します。
