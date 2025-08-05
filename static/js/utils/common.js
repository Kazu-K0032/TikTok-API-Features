/**
 * 共通JavaScriptユーティリティ
 */

/**
 * ファイルサイズをフォーマット
 * @param {number} bytes - バイト数
 * @returns {string} フォーマットされたファイルサイズ文字列
 */
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

/**
 * 文字数カウントを更新
 * @param {HTMLTextAreaElement} textarea - テキストエリア要素
 * @param {HTMLElement} charCountElement - 文字数表示要素
 * @param {number} maxLength - 最大文字数
 */
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

/**
 * ファイル情報を表示
 * @param {File} file - ファイルオブジェクト
 * @param {HTMLElement} fileInfoElement - ファイル情報表示要素
 * @param {HTMLElement} fileNameElement - ファイル名表示要素
 * @param {HTMLElement} fileSizeElement - ファイルサイズ表示要素
 * @param {HTMLElement} fileTypeElement - ファイルタイプ表示要素
 */
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

/**
 * APIリクエストの共通処理
 * @param {string} url - リクエストURL
 * @param {Object} options - リクエストオプション
 * @returns {Promise<Object>} APIレスポンス
 */
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
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        `HTTP ${response.status}: ${response.statusText} - ${
          errorData.error || ""
        }`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
}

/**
 * エラーメッセージを表示
 * @param {string} message - エラーメッセージ
 * @param {HTMLElement} container - 表示するコンテナ要素
 */
function showError(message, container) {
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.textContent = message;
  container.appendChild(errorDiv);

  setTimeout(() => {
    errorDiv.remove();
  }, UI_CONFIG.TOAST_DURATION);
}

/**
 * 成功メッセージを表示
 * @param {string} message - 成功メッセージ
 * @param {HTMLElement} container - 表示するコンテナ要素
 */
function showSuccess(message, container) {
  const successDiv = document.createElement("div");
  successDiv.className = "success-message";
  successDiv.textContent = message;
  container.appendChild(successDiv);

  setTimeout(() => {
    successDiv.remove();
  }, UI_CONFIG.TOAST_DURATION);
}

/**
 * ローディング状態を管理
 * @param {HTMLElement} element - 対象要素
 * @param {boolean} isLoading - ローディング状態
 * @param {string} loadingText - ローディング時のテキスト
 */
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

/**
 * エラーハンドリングの改善
 * @param {Error} error - エラーオブジェクト
 * @param {string} context - エラーコンテキスト
 * @returns {string} 処理されたエラーメッセージ
 */
function handleError(error, context = "") {
  let errorMessage = ERROR_MESSAGES.SERVER_ERROR;

  if (error.name === "TypeError" && error.message.includes("Failed to fetch")) {
    errorMessage = ERROR_MESSAGES.NETWORK_ERROR;
  } else if (error.message.includes("HTTP 401")) {
    errorMessage = ERROR_MESSAGES.UNAUTHORIZED;
  } else if (error.message.includes("HTTP 403")) {
    errorMessage = ERROR_MESSAGES.FORBIDDEN;
  } else if (error.message.includes("HTTP 404")) {
    errorMessage = ERROR_MESSAGES.NOT_FOUND;
  } else if (error.message.includes("HTTP 413")) {
    errorMessage = "ファイルサイズが大きすぎます。";
  } else if (error.message.includes("HTTP 429")) {
    errorMessage =
      "リクエストが多すぎます。しばらく時間をおいてから再試行してください。";
  } else if (error.message) {
    errorMessage = error.message;
  }

  if (context) {
    console.error(`${context}:`, error);
  }

  return errorMessage;
}

/**
 * ファイルバリデーション
 * @param {File} file - 検証するファイル
 * @param {number} maxSize - 最大ファイルサイズ
 * @param {Array<string>} allowedTypes - 許可されるファイルタイプ
 * @returns {Object} バリデーション結果 {valid: boolean, errors: Array<string>}
 */
function validateFile(
  file,
  maxSize = APP_CONFIG.MAX_FILE_SIZE,
  allowedTypes = APP_CONFIG.SUPPORTED_VIDEO_TYPES
) {
  const errors = [];

  if (!file) {
    errors.push("ファイルが選択されていません。");
    return { valid: false, errors };
  }

  if (file.size > maxSize) {
    errors.push(
      `ファイルサイズが大きすぎます。${formatFileSize(
        maxSize
      )}以下にしてください。`
    );
  }

  if (!allowedTypes.includes(file.type)) {
    errors.push("サポートされていないファイル形式です。");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
