/**
 * 動画アップロードページ用JavaScript
 */

// 投稿間隔制限（5分間）
let lastUploadTime = 0;
const UPLOAD_COOLDOWN = 5 * 60 * 1000; // 5分（ミリ秒）

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("video-file");
  const titleInput = document.getElementById("video-title");
  const charCount = document.getElementById("char-count");
  const fileInfo = document.getElementById("file-info");
  const progressDiv = document.getElementById("upload-progress");
  const resultDiv = document.getElementById("upload-result");

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
      '<span class="btn-icon">📤</span><span class="btn-text">アップロード</span>';
  }

  // ファイル選択時の処理
  fileInput.addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (file) {
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

  // フォーム送信処理
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    console.log("フォーム送信処理開始");

    // バリデーション
    if (!validateForm()) {
      console.log("バリデーションエラーによりフォーム送信をキャンセル");
      return;
    }

    // 投稿間隔チェック
    if (!checkUploadCooldown()) {
      console.log("投稿間隔制限によりフォーム送信をキャンセル");
      return;
    }

    const formData = new FormData(form);

    // ボタンを無効化
    setLoadingState(
      uploadBtn,
      true,
      '<span class="btn-icon">⏳</span><span class="btn-text">アップロード中...</span>'
    );

    // 進捗表示
    const progressDiv = document.getElementById("upload-progress");
    const formElement = document.getElementById("upload-form");
    if (progressDiv && formElement) {
      progressDiv.style.display = "block";
      formElement.style.display = "none";
    }

    console.log("直接投稿API呼び出し");
    // アップロード実行
    uploadVideo(formData);
  });

  // 別の動画をアップロード
  document
    .getElementById("upload-another")
    .addEventListener("click", function () {
      resultDiv.style.display = "none";
      form.style.display = "block";
      form.reset();
      fileInfo.style.display = "none";
      charCount.textContent = "0";
      charCount.style.color = "#666";

      // アップロードボタンの状態をリセット
      setLoadingState(uploadBtn, false);
      uploadBtn.innerHTML =
        '<span class="btn-icon">📤</span><span class="btn-text">直接投稿</span>';

      // プライバシー設定をデフォルトに戻す
      const privacySelect = document.getElementById("privacy-level");
      privacySelect.value = "";

      // ユーザー同意チェックボックスをリセット
      const userConsent = document.getElementById("user-consent");
      if (userConsent) {
        userConsent.checked = false;
      }
    });
});

// 動画アップロード処理（直接投稿）
function uploadVideo(formData) {
  console.log("直接投稿開始");

  // 進捗表示の初期化（フォーム送信時に行われているため、ここでは不要）
  console.log("直接投稿API呼び出し");
  uploadVideoToAPI(formData, "/api/upload-video", "直接投稿");
}

// 下書き投稿処理
function uploadDraft() {
  console.log("下書き投稿開始");

  const form = document.getElementById("upload-form");
  const formData = new FormData(form);

  // バリデーション
  if (!validateForm()) {
    console.log("バリデーションエラーにより下書き投稿をキャンセル");
    return;
  }

  // 投稿間隔チェック
  if (!checkUploadCooldown()) {
    console.log("投稿間隔制限により下書き投稿をキャンセル");
    return;
  }

  // ボタンを無効化
  const uploadDraftBtn = document.getElementById("upload-draft-btn");
  setLoadingState(
    uploadDraftBtn,
    true,
    '<span class="btn-icon">⏳</span><span class="btn-text">下書き投稿中...</span>'
  );

  // 進捗表示
  const progressDiv = document.getElementById("upload-progress");
  const formElement = document.getElementById("upload-form");
  progressDiv.style.display = "block";
  formElement.style.display = "none";

  uploadVideoToAPI(formData, "/api/upload-draft", "下書き投稿");
}

// 共通の動画アップロード処理
function uploadVideoToAPI(formData, endpoint, uploadType) {
  console.log(`${uploadType} 開始: ${endpoint}`);

  const progressStatus = document.getElementById("progress-status");
  const progressFill = document.getElementById("progress-fill");
  const progressText = document.getElementById("progress-text");

  // 進捗初期化
  updateProgress(0, `${uploadType}リクエスト送信中...`);
  console.log(`${uploadType} 進捗: 0% - リクエスト送信中`);

  fetch(endpoint, {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      // レスポンス受信時
      updateProgress(20, `${uploadType}サーバー処理中...`);
      console.log(`${uploadType} 進捗: 20% - サーバー処理中`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    })
    .then((data) => {
      // データ処理中
      updateProgress(60, `${uploadType}結果確認中...`);
      console.log(`${uploadType} 進捗: 60% - 結果確認中`);

      if (data.success) {
        // 成功時
        updateProgress(100, `${uploadType}完了`);
        console.log(`${uploadType} 進捗: 100% - 完了`);
        // 成功時は投稿時間を記録
        lastUploadTime = Date.now();
        setTimeout(() => {
          showResult(true, "アップロード完了", data.message);
        }, 500);
      } else {
        // エラー時
        updateProgress(100, `${uploadType}エラー`);
        console.log(`${uploadType} 進捗: 100% - エラー`);
        let errorMessage = data.error;
        if (errorMessage.includes("Content Posting API")) {
          errorMessage =
            "Content Posting APIの権限が不足しています。アプリの設定でContent Posting APIを有効にしてください。";
        } else if (errorMessage.includes("未監査クライアント")) {
          errorMessage =
            "未監査クライアントはプライベートアカウントのみに投稿できます。TikTokアプリでアカウントをプライベート設定に変更してください。";
        } else if (errorMessage.includes("spam_risk_too_many_pending_share")) {
          errorMessage =
            "投稿頻度が高すぎます。しばらく時間をおいてから再度お試しください。\n\n" +
            "【対処法】\n" +
            "• 数分間待ってから再度投稿してください\n" +
            "• TikTokアプリで既存の下書きを確認・削除してください\n" +
            "• 投稿間隔を空けてください";
        }
        showResult(false, "アップロード失敗", errorMessage);
      }
    })
    .catch((error) => {
      console.error("アップロードエラー:", error);
      updateProgress(100, `${uploadType}エラー`);
      console.log(`${uploadType} 進捗: 100% - ネットワークエラー`);

      let errorMessage = "ネットワークエラーが発生しました。";

      // より詳細なエラー情報を表示
      if (
        error.name === "TypeError" &&
        error.message.includes("Failed to fetch")
      ) {
        errorMessage =
          "サーバーに接続できません。サーバーが起動しているか確認してください。";
      } else if (error.message) {
        errorMessage = `エラー詳細: ${error.message}`;
      }

      setTimeout(() => {
        showResult(false, "アップロード失敗", errorMessage);
      }, 500);
    })
    .finally(() => {
      // エラー発生時もボタンの状態をリセット
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
    });
}

// 進捗更新関数
function updateProgress(percentage, status) {
  const progressStatus = document.getElementById("progress-status");
  const progressFill = document.getElementById("progress-fill");
  const progressText = document.getElementById("progress-text");

  if (progressStatus) progressStatus.textContent = status;
  if (progressFill) progressFill.style.width = percentage + "%";
  if (progressText) progressText.textContent = percentage + "%";
}

// 結果表示処理
function showResult(success, title, message) {
  const progressDiv = document.getElementById("upload-progress");
  const resultDiv = document.getElementById("upload-result");
  const resultIcon = document.getElementById("result-icon");
  const resultTitle = document.getElementById("result-title");
  const resultMessage = document.getElementById("result-message");

  progressDiv.style.display = "none";
  resultDiv.style.display = "block";

  if (success) {
    resultIcon.textContent = "✅";
    resultIcon.style.color = "#4CAF50";

    // 下書き投稿の場合は特別なメッセージを表示
    if (
      title === "アップロード完了" &&
      (message.includes("下書き") || message.includes("TikTokの下書き"))
    ) {
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

      resultMessage.innerHTML = formattedMessage;
    } else {
      resultMessage.textContent = message;
    }
  } else {
    resultIcon.textContent = "❌";
    resultIcon.style.color = "#f44336";
    resultMessage.textContent = message;
  }

  resultTitle.textContent = title;
}

// 投稿間隔チェック
function checkUploadCooldown() {
  const now = Date.now();
  const timeSinceLastUpload = now - lastUploadTime;

  console.log(
    `投稿間隔チェック: 前回投稿から${Math.ceil(
      timeSinceLastUpload / 1000 / 60
    )}分経過`
  );

  if (timeSinceLastUpload < UPLOAD_COOLDOWN) {
    const remainingTime = Math.ceil(
      (UPLOAD_COOLDOWN - timeSinceLastUpload) / 1000 / 60
    );
    console.log(`投稿間隔制限: あと${remainingTime}分待機が必要`);
    alert(
      `投稿間隔が短すぎます。${remainingTime}分後に再度お試しください。\n\n【理由】\n• TikTokのスパム対策により、短時間での連続投稿が制限されています\n• 投稿間隔を空けることで、エラーを回避できます`
    );
    return false;
  }

  console.log("投稿間隔チェック: OK");
  return true;
}

// フォームバリデーション
function validateForm() {
  console.log("フォームバリデーション開始");

  const privacyLevel = document.getElementById("privacy-level").value;
  const userConsent = document.getElementById("user-consent");

  if (!privacyLevel) {
    console.log("バリデーションエラー: プライバシー設定が選択されていません");
    alert("プライバシー設定を選択してください。");
    return false;
  }

  if (!userConsent || !userConsent.checked) {
    console.log("バリデーションエラー: 音楽使用確認に同意していません");
    alert("TikTokの音楽使用確認に同意してください。");
    return false;
  }

  console.log("フォームバリデーション完了");
  return true;
}
