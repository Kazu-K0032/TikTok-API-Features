/**
 * 共通JavaScriptユーティリティ
 */

// ファイルサイズのフォーマット
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// 文字数カウントの更新
function updateCharCount(
  textarea,
  charCountElement,
  maxLength = APP_CONFIG.MAX_TITLE_LENGTH
) {
  const count = textarea.value.length;
  charCountElement.textContent = count;

  if (count > maxLength * 0.9) {
    charCountElement.style.color = COLORS.ERROR;
  } else if (count > maxLength * 0.8) {
    charCountElement.style.color = COLORS.WARNING;
  } else {
    charCountElement.style.color = COLORS.GRAY;
  }
}

// ファイル情報の表示
function displayFileInfo(
  file,
  fileInfoElement,
  fileNameElement,
  fileSizeElement,
  fileTypeElement
) {
  if (file) {
    fileNameElement.textContent = file.name;
    fileSizeElement.textContent = formatFileSize(file.size);
    fileTypeElement.textContent = file.type;
    fileInfoElement.style.display = "block";
  } else {
    fileInfoElement.style.display = "none";
  }
}

// APIリクエストの共通処理
async function makeApiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      timeout: API_CONFIG.TIMEOUT,
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
}

// エラーメッセージの表示
function showError(message, container) {
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.textContent = message;
  container.appendChild(errorDiv);

  setTimeout(() => {
    errorDiv.remove();
  }, UI_CONFIG.TOAST_DURATION);
}

// 成功メッセージの表示
function showSuccess(message, container) {
  const successDiv = document.createElement("div");
  successDiv.className = "success-message";
  successDiv.textContent = message;
  container.appendChild(successDiv);

  setTimeout(() => {
    successDiv.remove();
  }, UI_CONFIG.TOAST_DURATION);
}

// ローディング状態の管理
function setLoadingState(element, isLoading, loadingText = "読み込み中...") {
  if (isLoading) {
    element.disabled = true;
    element.dataset.originalText = element.textContent;
    element.textContent = loadingText;
  } else {
    element.disabled = false;
    if (element.dataset.originalText) {
      element.textContent = element.dataset.originalText;
      delete element.dataset.originalText;
    }
  }
}
