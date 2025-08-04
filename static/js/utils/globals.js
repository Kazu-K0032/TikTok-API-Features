/**
 * グローバル変数定義
 */

// API設定
const API_CONFIG = {
  BASE_URL: "",
  ENDPOINTS: {
    SWITCH_USER: "/api/switch-user",
    REMOVE_USER: "/api/remove-user",
    USER_DATA: "/api/user-data",
    USERS: "/api/users",
    UPLOAD_VIDEO: "/api/upload-video",
  },
  TIMEOUT: 30000,
};

// アプリケーション設定
const APP_CONFIG = {
  MAX_TITLE_LENGTH: 2200,
  MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
  SUPPORTED_VIDEO_TYPES: ["video/mp4", "video/avi", "video/mov", "video/wmv"],
  CHUNK_SIZE: 1024 * 1024, // 1MB
};

// UI設定
const UI_CONFIG = {
  ANIMATION_DURATION: 300,
  TOAST_DURATION: 3000,
  LOADING_DELAY: 500,
};

// エラーメッセージ
const ERROR_MESSAGES = {
  NETWORK_ERROR: "ネットワークエラーが発生しました。",
  UPLOAD_FAILED: "アップロードに失敗しました。",
  VALIDATION_ERROR: "入力内容を確認してください。",
  API_ERROR: "APIエラーが発生しました。",
  UNAUTHORIZED: "認証が必要です。",
  FORBIDDEN: "アクセス権限がありません。",
  NOT_FOUND: "リソースが見つかりません。",
  SERVER_ERROR: "サーバーエラーが発生しました。",
};

// 成功メッセージ
const SUCCESS_MESSAGES = {
  UPLOAD_COMPLETE: "アップロードが完了しました。",
  USER_SWITCHED: "ユーザーを切り替えました。",
  USER_REMOVED: "ユーザーを削除しました。",
  SETTINGS_SAVED: "設定を保存しました。",
};

// ステータスコード
const STATUS_CODES = {
  SUCCESS: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
};

// カラーコード
const COLORS = {
  PRIMARY: "#ff0050",
  SECONDARY: "#e6004c",
  SUCCESS: "#4CAF50",
  WARNING: "#ff6b35",
  ERROR: "#f44336",
  INFO: "#2196F3",
  LIGHT_GRAY: "#f5f5f5",
  GRAY: "#666",
  DARK_GRAY: "#333",
  WHITE: "#ffffff",
  BLACK: "#000000",
};

// フォント設定
const FONTS = {
  PRIMARY:
    'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  MONOSPACE: 'Consolas, Monaco, "Courier New", monospace',
};

// ブレークポイント
const BREAKPOINTS = {
  MOBILE: 768,
  TABLET: 1024,
  DESKTOP: 1200,
};

// ローカルストレージキー
const STORAGE_KEYS = {
  USER_PREFERENCES: "tiktok_api_user_preferences",
  UPLOAD_HISTORY: "tiktok_api_upload_history",
  THEME: "tiktok_api_theme",
};

// デフォルト設定
const DEFAULTS = {
  PRIVACY_LEVEL: "SELF_ONLY",
  DISABLE_COMMENT: false,
  DISABLE_DUET: false,
  DISABLE_STITCH: false,
  THEME: "light",
};
