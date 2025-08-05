/**
 * 動画アップロードページ用JavaScript
 */

/**
 * モジュールパターンでアップロード管理
 */
const UploadManager = {
  // 状態管理
  state: {
    lastUploadTime: 0,
    UPLOAD_COOLDOWN: 5 * 60 * 1000, // 5分（ミリ秒）
    MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
    SUPPORTED_TYPES: ["video/mp4", "video/avi", "video/mov", "video/wmv"],
  },

  // エラーメッセージ管理
  errorMessages: {
    NETWORK_ERROR: "ネットワークエラーが発生しました。",
    UPLOAD_FAILED: "アップロードに失敗しました。",
    VALIDATION_ERROR: "入力内容を確認してください。",
    FILE_TOO_LARGE: "ファイルサイズが大きすぎます。100MB以下にしてください。",
    UNSUPPORTED_FILE_TYPE: "サポートされていないファイル形式です。",
    PRIVACY_RESTRICTION:
      "未監査アプリケーションでは「自分だけ」の設定でのみ投稿可能です。",
    UPLOAD_COOLDOWN: "投稿間隔が短すぎます。5分後に再度お試しください。",
    SERVER_CONNECTION_ERROR:
      "サーバーに接続できません。サーバーが起動しているか確認してください。",
    CONTENT_POSTING_API_ERROR:
      "Content Posting APIの権限が不足しています。アプリの設定でContent Posting APIを有効にしてください。",
    PRIVATE_ACCOUNT_REQUIRED:
      "未監査クライアントはプライベートアカウントのみに投稿できます。TikTokアプリでアカウントをプライベート設定に変更してください。",
    SPAM_RISK_ERROR:
      "投稿頻度が高すぎます。しばらく時間をおいてから再度お試しください。",
  },

  /**
   * ファイル検証
   * @param {File} file - 検証するファイル
   * @returns {Object} 検証結果 {valid: boolean, error?: string}
   */
  validateFile(file) {
    if (!file) {
      return { valid: false, error: this.errorMessages.VALIDATION_ERROR };
    }

    if (file.size > this.state.MAX_FILE_SIZE) {
      return { valid: false, error: this.errorMessages.FILE_TOO_LARGE };
    }

    if (!this.state.SUPPORTED_TYPES.includes(file.type)) {
      return { valid: false, error: this.errorMessages.UNSUPPORTED_FILE_TYPE };
    }

    return { valid: true };
  },

  /**
   * 投稿間隔チェック
   * @returns {boolean} 投稿可能かどうか
   */
  checkUploadCooldown() {
    const now = Date.now();
    const timeSinceLastUpload = now - this.state.lastUploadTime;

    if (timeSinceLastUpload < this.state.UPLOAD_COOLDOWN) {
      const remainingTime = Math.ceil(
        (this.state.UPLOAD_COOLDOWN - timeSinceLastUpload) / 1000 / 60
      );
      alert(
        `${this.errorMessages.UPLOAD_COOLDOWN}\n\n【理由】\n• TikTokのスパム対策により、短時間での連続投稿が制限されています\n• 投稿間隔を空けることで、エラーを回避できます`
      );
      return false;
    }

    return true;
  },

  /**
   * 投稿時間を記録
   */
  recordUploadTime() {
    this.state.lastUploadTime = Date.now();
  },
};

/**
 * 進捗管理モジュール
 */
const ProgressManager = {
  /**
   * 進捗バーを更新
   * @param {number} percentage - 進捗率（0-100）
   * @param {string} status - ステータスメッセージ
   */
  updateProgress(percentage, status) {
    const progressStatus = document.getElementById("progress-status");
    const progressFill = document.getElementById("progress-fill");
    const progressText = document.getElementById("progress-text");

    if (progressStatus) progressStatus.textContent = status;
    if (progressFill) progressFill.style.width = percentage + "%";
    if (progressText) progressText.textContent = percentage + "%";
  },

  /**
   * 進捗表示を表示
   */
  showProgress() {
    const progressDiv = document.getElementById("upload-progress");
    const formElement = document.getElementById("upload-form");
    if (progressDiv && formElement) {
      progressDiv.style.display = "block";
      formElement.style.display = "none";
    }
  },

  /**
   * 進捗表示を非表示
   */
  hideProgress() {
    const progressDiv = document.getElementById("upload-progress");
    if (progressDiv) {
      progressDiv.style.display = "none";
    }
  },
};

/**
 * フォーム管理モジュール
 */
const FormManager = {
  /**
   * フォームバリデーション
   * @returns {boolean} バリデーション結果
   */
  validateForm() {
    const privacyLevel = document.getElementById("privacy-level").value;
    const userConsent = document.getElementById("user-consent");

    if (!privacyLevel) {
      alert("プライバシー設定を選択してください。");
      return false;
    }

    if (!userConsent || !userConsent.checked) {
      alert("TikTokの音楽使用確認に同意してください。");
      return false;
    }

    return true;
  },

  /**
   * フォームをリセット
   */
  resetForm() {
    const form = document.getElementById("upload-form");
    const fileInfo = document.getElementById("file-info");
    const charCount = document.getElementById("char-count");
    const uploadBtn = document.getElementById("upload-btn");

    if (form) form.reset();
    if (fileInfo) fileInfo.style.display = "none";
    if (charCount) {
      charCount.textContent = "0";
      charCount.style.color = "#666";
    }
    if (uploadBtn) {
      uploadBtn.disabled = false;
      uploadBtn.innerHTML =
        '<span class="btn-icon">📤</span><span class="btn-text">直接投稿</span>';
    }

    // プライバシー設定をデフォルトに戻す
    const privacySelect = document.getElementById("privacy-level");
    if (privacySelect) privacySelect.value = "";

    // ユーザー同意チェックボックスをリセット
    const userConsent = document.getElementById("user-consent");
    if (userConsent) userConsent.checked = false;
  },
};

/**
 * 結果表示モジュール
 */
const ResultManager = {
  /**
   * 結果を表示
   * @param {boolean} success - 成功かどうか
   * @param {string} title - タイトル
   * @param {string} message - メッセージ
   */
  showResult(success, title, message) {
    const progressDiv = document.getElementById("upload-progress");
    const resultDiv = document.getElementById("upload-result");
    const resultIcon = document.getElementById("result-icon");
    const resultTitle = document.getElementById("result-title");
    const resultMessage = document.getElementById("result-message");

    ProgressManager.hideProgress();
    if (resultDiv) resultDiv.style.display = "block";

    if (success) {
      if (resultIcon) {
        resultIcon.textContent = "✅";
        resultIcon.style.color = "#4CAF50";
      }

      // 下書き投稿の場合は特別なメッセージを表示
      if (
        title === "アップロード完了" &&
        (message.includes("下書き") || message.includes("TikTokの下書き"))
      ) {
        if (resultMessage) {
          resultMessage.innerHTML = `
            <p>下書き投稿が完了しました。</p>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
              <h4 style="margin-top: 0; color: #495057;">📱 下書き投稿について</h4>
              <ul style="margin: 10px 0; padding-left: 20px; list-style-type: none;">
                <li><strong>下書き投稿はPCやWebブラウザでは表示されない仕様</strong>です</li>
                <li>スマホの「メッセージ」→「システム通知」から投稿を進めることができます</li>
              </ul>
            </div>
          `;
        }
      } else if (message.includes("プロフィール:")) {
        // 直接投稿の場合はプロフィールリンクをクリック可能にする
        const lines = message.split("\n");
        let formattedMessage = "";
        let profileLink = "";

        lines.forEach((line) => {
          if (line.startsWith("プロフィール:")) {
            const link = line.replace("プロフィール: ", "");
            profileLink = link;
            formattedMessage += line + "<br>";
          } else {
            formattedMessage += line + "<br>";
          }
        });

        // プロフィールを開くボタンを追加
        if (profileLink) {
          formattedMessage += `<br><a href="${profileLink}" target="_blank" class="btn btn-primary profile-btn">プロフィールを開く</a>`;
        }

        if (resultMessage) resultMessage.innerHTML = formattedMessage;
      } else {
        if (resultMessage) resultMessage.textContent = message;
      }
    } else {
      if (resultIcon) {
        resultIcon.textContent = "❌";
        resultIcon.style.color = "#f44336";
      }
      if (resultMessage) resultMessage.textContent = message;
    }

    if (resultTitle) resultTitle.textContent = title;
  },
};

/**
 * API通信モジュール
 */
const ApiManager = {
  /**
   * 動画をアップロード
   * @param {FormData} formData - フォームデータ
   * @param {string} endpoint - APIエンドポイント
   * @param {string} uploadType - アップロードタイプ
   * @returns {Promise<void>}
   */
  async uploadVideo(formData, endpoint, uploadType) {
    ProgressManager.updateProgress(0, `${uploadType}リクエスト送信中...`);

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      ProgressManager.updateProgress(20, `${uploadType}サーバー処理中...`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      ProgressManager.updateProgress(60, `${uploadType}結果確認中...`);

      if (data.success) {
        ProgressManager.updateProgress(100, `${uploadType}完了`);
        UploadManager.recordUploadTime();
        setTimeout(() => {
          ResultManager.showResult(true, "アップロード完了", data.message);
        }, 500);
      } else {
        ProgressManager.updateProgress(100, `${uploadType}エラー`);
        const errorMessage = this.handleApiError(data.error);
        setTimeout(() => {
          ResultManager.showResult(false, "アップロード失敗", errorMessage);
        }, 500);
      }
    } catch (error) {
      ProgressManager.updateProgress(100, `${uploadType}エラー`);
      const errorMessage = this.handleNetworkError(error);
      setTimeout(() => {
        ResultManager.showResult(false, "アップロード失敗", errorMessage);
      }, 500);
    } finally {
      this.resetButtons();
    }
  },

  /**
   * APIエラーを処理
   * @param {string} errorMessage - エラーメッセージ
   * @returns {string} 処理されたエラーメッセージ
   */
  handleApiError(errorMessage) {
    if (errorMessage.includes("Content Posting API")) {
      return UploadManager.errorMessages.CONTENT_POSTING_API_ERROR;
    } else if (errorMessage.includes("未監査クライアント")) {
      return UploadManager.errorMessages.PRIVATE_ACCOUNT_REQUIRED;
    } else if (errorMessage.includes("spam_risk_too_many_pending_share")) {
      return (
        UploadManager.errorMessages.SPAM_RISK_ERROR +
        "\n\n【対処法】\n• 数分間待ってから再度投稿してください\n• TikTokアプリで既存の下書きを確認・削除してください\n• 投稿間隔を空けてください"
      );
    }
    return errorMessage;
  },

  /**
   * ネットワークエラーを処理
   * @param {Error} error - エラーオブジェクト
   * @returns {string} 処理されたエラーメッセージ
   */
  handleNetworkError(error) {
    if (
      error.name === "TypeError" &&
      error.message.includes("Failed to fetch")
    ) {
      return UploadManager.errorMessages.SERVER_CONNECTION_ERROR;
    } else if (error.message) {
      return `エラー詳細: ${error.message}`;
    }
    return UploadManager.errorMessages.NETWORK_ERROR;
  },

  /**
   * ボタンの状態をリセット
   */
  resetButtons() {
    const uploadBtn = document.getElementById("upload-btn");
    const uploadDraftBtn = document.getElementById("upload-draft-btn");

    if (uploadBtn) {
      setLoadingState(uploadBtn, false);
      uploadBtn.innerHTML =
        '<span class="btn-icon">📤</span><span class="btn-text">直接投稿</span>';
    }

    if (uploadDraftBtn) {
      setLoadingState(uploadDraftBtn, false);
      uploadDraftBtn.innerHTML =
        '<span class="btn-icon">📝</span><span class="btn-text">下書き投稿</span>';
    }
  },
};

// メイン処理
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("video-file");
  const titleInput = document.getElementById("video-title");
  const charCount = document.getElementById("char-count");
  const fileInfo = document.getElementById("file-info");

  // 下書き投稿ボタンのイベントリスナー
  const uploadDraftBtn = document.getElementById("upload-draft-btn");
  if (uploadDraftBtn) {
    uploadDraftBtn.addEventListener("click", uploadDraft);
  }

  // ページ読み込み時にアップロードボタンの状態をリセット
  const uploadBtn = document.getElementById("upload-btn");
  if (uploadBtn) {
    uploadBtn.disabled = false;
    uploadBtn.innerHTML =
      '<span class="btn-icon">📤</span><span class="btn-text">直接投稿</span>';
  }

  // ファイル選択時の処理
  fileInput.addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (file) {
      const validation = UploadManager.validateFile(file);
      if (!validation.valid) {
        alert(validation.error);
        this.value = "";
        return;
      }

      const fileName = document.getElementById("file-name");
      const fileSize = document.getElementById("file-size");
      const fileType = document.getElementById("file-type");

      displayFileInfo(file, fileInfo, fileName, fileSize, fileType);
    }
  });

  // キャプション入力時の文字数カウント
  titleInput.addEventListener("input", function () {
    updateCharCount(titleInput, charCount);
  });

  // プライバシー設定の制限（未監査アプリでは「自分だけ」のみ選択可能）
  const privacySelect = document.getElementById("privacy-level");
  if (privacySelect) {
    privacySelect.addEventListener("change", function () {
      const selectedValue = this.value;
      if (selectedValue && selectedValue !== "SELF_ONLY") {
        alert(UploadManager.errorMessages.PRIVACY_RESTRICTION);
        this.value = "SELF_ONLY";
      }
    });
  }

  // フォーム送信処理
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    if (!FormManager.validateForm()) {
      return;
    }

    if (!UploadManager.checkUploadCooldown()) {
      return;
    }

    const formData = new FormData(form);

    // ボタンを無効化
    setLoadingState(
      uploadBtn,
      true,
      '<span class="btn-icon">⏳</span><span class="btn-text">アップロード中...</span>'
    );

    ProgressManager.showProgress();
    uploadVideo(formData);
  });

  // 別の動画をアップロード
  document
    .getElementById("upload-another")
    .addEventListener("click", function () {
      const resultDiv = document.getElementById("upload-result");
      const formElement = document.getElementById("upload-form");

      if (resultDiv) resultDiv.style.display = "none";
      if (formElement) formElement.style.display = "block";

      FormManager.resetForm();
    });
});

// 動画アップロード処理（直接投稿）
function uploadVideo(formData) {
  ApiManager.uploadVideo(formData, "/api/upload-video", "直接投稿");
}

// 下書き投稿処理
function uploadDraft() {
  const form = document.getElementById("upload-form");
  const formData = new FormData(form);

  if (!FormManager.validateForm()) {
    return;
  }

  if (!UploadManager.checkUploadCooldown()) {
    return;
  }

  // ボタンを無効化
  const uploadDraftBtn = document.getElementById("upload-draft-btn");
  setLoadingState(
    uploadDraftBtn,
    true,
    '<span class="btn-icon">⏳</span><span class="btn-text">下書き投稿中...</span>'
  );

  ProgressManager.showProgress();
  ApiManager.uploadVideo(formData, "/api/upload-draft", "下書き投稿");
}
