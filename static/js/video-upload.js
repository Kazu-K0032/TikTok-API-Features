/**
 * 動画アップロードページ用JavaScript
 */

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("video-file");
  const titleInput = document.getElementById("video-title");
  const charCount = document.getElementById("char-count");
  const fileInfo = document.getElementById("file-info");
  const progressDiv = document.getElementById("upload-progress");
  const resultDiv = document.getElementById("upload-result");

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

    // バリデーション
    const privacyLevel = document.getElementById("privacy-level").value;
    const userConsent = document.getElementById("user-consent");

    if (!privacyLevel) {
      alert("プライバシー設定を選択してください。");
      return;
    }

    if (!userConsent || !userConsent.checked) {
      alert("TikTokの音楽使用確認に同意してください。");
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
    progressDiv.style.display = "block";
    form.style.display = "none";

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
        '<span class="btn-icon">📤</span><span class="btn-text">アップロード</span>';

      // プライバシー設定をデフォルトに戻す
      const privacySelect = document.getElementById("privacy-level");
      privacySelect.value = "";

      // ユーザー同意チェックボックスをリセット
      if (userConsent) {
        userConsent.checked = false;
      }
    });
});

// 動画アップロード処理
function uploadVideo(formData) {
  const progressStatus = document.getElementById("progress-status");
  const progressFill = document.getElementById("progress-fill");
  const progressText = document.getElementById("progress-text");

  fetch("/api/upload-video", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showResult(true, "アップロード完了", data.message);
      } else {
        let errorMessage = data.error;
        if (errorMessage.includes("Content Posting API")) {
          errorMessage =
            "Content Posting APIの権限が不足しています。アプリの設定でContent Posting APIを有効にしてください。";
        } else if (errorMessage.includes("未監査クライアント")) {
          errorMessage =
            "未監査クライアントはプライベートアカウントのみに投稿できます。TikTokアプリでアカウントをプライベート設定に変更してください。";
        }
        showResult(false, "アップロード失敗", errorMessage);
      }
    })
    .catch((error) => {
      console.error("アップロードエラー:", error);
      showResult(
        false,
        "アップロード失敗",
        "ネットワークエラーが発生しました。"
      );
    })
    .finally(() => {
      // エラー発生時もボタンの状態をリセット
      const uploadBtn = document.getElementById("upload-btn");
      if (uploadBtn) {
        setLoadingState(uploadBtn, false);
        uploadBtn.innerHTML =
          '<span class="btn-icon">📤</span><span class="btn-text">アップロード</span>';
      }
    });
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

    // 成功時はプロフィールリンクをクリック可能にする
    if (message.includes("プロフィール:")) {
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
}
