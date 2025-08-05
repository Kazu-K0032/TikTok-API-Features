/**
 * ダッシュボードページ用JavaScript
 */

// ページネーション状態管理
const PaginationManager = {
  currentPage: 1,
  itemsPerPage: 6,
  totalItems: 0,
  totalPages: 0,
  currentVideos: [],

  /**
   * ページネーションを初期化
   * @param {Array} videos - 全動画配列
   */
  init(videos) {
    this.currentVideos = videos || [];
    this.totalItems = this.currentVideos.length;
    this.totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
    this.currentPage = 1;
  },

  /**
   * 現在のページの動画を取得
   * @returns {Array} 現在のページの動画配列
   */
  getCurrentPageVideos() {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.currentVideos.slice(startIndex, endIndex);
  },

  /**
   * 指定ページに移動
   * @param {number} page - 移動先ページ番号
   */
  goToPage(page) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.updateDisplay();
    }
  },

  /**
   * 前のページに移動
   */
  goToPreviousPage() {
    if (this.currentPage > 1) {
      this.goToPage(this.currentPage - 1);
    }
  },

  /**
   * 次のページに移動
   */
  goToNextPage() {
    if (this.currentPage < this.totalPages) {
      this.goToPage(this.currentPage + 1);
    }
  },

  /**
   * 表示を更新
   */
  updateDisplay() {
    const currentVideos = this.getCurrentPageVideos();
    updateVideoGrid(currentVideos);
    updatePaginationDisplay();
  },

  /**
   * ページネーション表示を更新
   */
  updatePaginationDisplay() {
    const paginationContainer = document.getElementById("pagination-container");
    if (!paginationContainer) return;

    if (this.totalPages <= 1) {
      paginationContainer.style.display = "none";
      return;
    }

    paginationContainer.style.display = "block";

    const paginationHTML = this.generatePaginationHTML();
    paginationContainer.innerHTML = paginationHTML;

    // イベントリスナーを追加
    this.addPaginationEventListeners();
  },

  /**
   * ページネーションHTMLを生成
   * @returns {string} ページネーションHTML
   */
  generatePaginationHTML() {
    const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
    const endItem = Math.min(
      this.currentPage * this.itemsPerPage,
      this.totalItems
    );

    let paginationHTML = `
      <div class="pagination-summary">
        ${startItem}-${endItem} / ${this.totalItems} 件表示
      </div>
      <div class="pagination">
        <button class="pagination-btn" data-action="prev" ${
          this.currentPage === 1 ? "disabled" : ""
        }>
          ← 前へ
        </button>
        <div class="pagination-pages">
    `;

    // ページ番号を表示（最大5ページまで）
    const maxVisiblePages = 5;
    let startPage = Math.max(
      1,
      this.currentPage - Math.floor(maxVisiblePages / 2)
    );
    let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      const isCurrent = i === this.currentPage;
      paginationHTML += `
        <a href="#" class="pagination-link ${
          isCurrent ? "pagination-current" : ""
        }" data-page="${i}">
          ${i}
        </a>
      `;
    }

    paginationHTML += `
        </div>
        <button class="pagination-btn" data-action="next" ${
          this.currentPage === this.totalPages ? "disabled" : ""
        }>
          次へ →
        </button>
      </div>
    `;

    return paginationHTML;
  },

  /**
   * ページネーションイベントリスナーを追加
   */
  addPaginationEventListeners() {
    // 前へ/次へボタン
    document.querySelectorAll(".pagination-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const action = btn.dataset.action;
        if (action === "prev") {
          this.goToPreviousPage();
        } else if (action === "next") {
          this.goToNextPage();
        }
      });
    });

    // ページ番号リンク
    document.querySelectorAll(".pagination-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const page = parseInt(link.dataset.page);
        this.goToPage(page);
      });
    });
  },
};

/**
 * ユーザーを切り替える（SPA風の機能）
 * @param {string} openId - 切り替え先ユーザーのOpen ID
 * @returns {Promise<void>}
 */
async function switchUser(openId) {
  try {
    // ローディング表示
    showLoading();

    const response = await makeApiRequest("/api/switch-user", {
      method: "POST",
      body: JSON.stringify({ open_id: openId }),
    });

    // ユーザーデータを取得
    const userDataResponse = await fetch(`/api/user-data?open_id=${openId}`);
    if (userDataResponse.ok) {
      const userData = await userDataResponse.json();
      updateDashboardContent(userData);
    } else {
      // データ取得に失敗した場合はページをリロード
      window.location.reload();
    }
  } catch (error) {
    console.error("ユーザー切り替えエラー:", error);
    alert("ユーザー切り替えに失敗しました");
  } finally {
    hideLoading();
  }
}

/**
 * ダッシュボードコンテンツを更新
 * @param {Object} userData - ユーザーデータオブジェクト
 * @param {Object} userData.profile - プロフィール情報
 * @param {Array} userData.videos - 動画リスト
 * @param {Object} userData.user_info - ユーザー統計情報
 */
function updateDashboardContent(userData) {
  const { profile, videos, user_info } = userData;

  // プロフィール情報を更新
  if (profile) {
    // アバター
    const avatar = document.getElementById("profile-avatar");
    if (avatar) {
      avatar.src = profile.avatar_url || "/static/images/default-avatar.svg";
    }

    // 表示名
    const name = document.getElementById("profile-name");
    if (name) {
      name.textContent = profile.display_name || "未設定";
    }

    // ユーザー名
    const username = document.getElementById("profile-username");
    if (username) {
      if (profile.username) {
        username.innerHTML = `<strong>ユーザー名:</strong> @${profile.username}`;
        username.style.display = "block";
      } else {
        username.style.display = "none";
      }
    }

    // Open ID
    const openId = document.getElementById("profile-openid");
    if (openId) {
      openId.textContent = profile.open_id || "未取得";
    }

    // 自己紹介
    const bio = document.getElementById("profile-bio");
    if (bio) {
      if (profile.bio_description) {
        bio.innerHTML = `<strong>自己紹介:</strong> ${profile.bio_description}`;
        bio.style.display = "block";
      } else {
        bio.style.display = "none";
      }
    }

    // 認証済み
    const verified = document.getElementById("profile-verified");
    if (verified) {
      verified.style.display = profile.is_verified ? "block" : "none";
    }

    // プロフィールリンク
    const link = document.getElementById("profile-link");
    if (link) {
      if (profile.profile_web_link) {
        link.innerHTML = `<a href="${profile.profile_web_link}" target="_blank">🌐 プロフィールページを開く</a>`;
        link.style.display = "block";
      } else {
        link.style.display = "none";
      }
    }

    // 統計情報を更新
    const followingCount = document.getElementById("following-count");
    if (followingCount) {
      followingCount.textContent = profile.following_count || 0;
    }

    const followerCount = document.getElementById("follower-count");
    if (followerCount) {
      followerCount.textContent = profile.follower_count || 0;
    }

    const likesCount = document.getElementById("likes-count");
    if (likesCount) {
      likesCount.textContent = profile.likes_count || 0;
    }

    const videoCount = document.getElementById("video-count");
    if (videoCount) {
      videoCount.textContent = profile.video_count || 0;
    }

    // 新しい統計情報を更新
    const totalViewCount = document.getElementById("total-view-count");
    if (totalViewCount) {
      totalViewCount.textContent = user_info.total_view_count || 0;
    }

    const shareCount = document.getElementById("share-count");
    if (shareCount) {
      shareCount.textContent = user_info.total_share_count || 0;
    }

    const avgEngagementRate = document.getElementById("avg-engagement-rate");
    if (avgEngagementRate) {
      avgEngagementRate.textContent = user_info.avg_engagement_rate || 0;
    }
  }

  // 動画リストを更新（ページネーション機能付き）
  if (videos) {
    PaginationManager.init(videos);
    PaginationManager.updateDisplay();
  }

  // ヘッダーのアクティブ状態を更新
  updateHeaderActiveState(user_info.open_id);
}

/**
 * 動画グリッドを更新
 * @param {Array} videos - 動画オブジェクトの配列
 */
function updateVideoGrid(videos) {
  const videoGrid = document.getElementById("video-grid");
  if (!videoGrid) return;

  if (videos.length === 0) {
    videoGrid.innerHTML = `
            <div class="card empty-state">
                <p class="empty-state-title">動画が見つかりませんでした</p>
                <p class="empty-state-description">
                    ※ 公開動画がないか、動画が存在しない可能性があります
                </p>
            </div>
        `;
    return;
  }

  const videoCards = videos
    .map(
      (video) => `
                <div class="video-card">
                    ${
                      video.best_image_url
                        ? `
                                <div class="video-thumbnail">
                                    <img
                                        src="${video.best_image_url}"
                                        alt="サムネイル"
                                        class="video-cover"
                                        loading="lazy"
                                    />
                                </div>
                            `
                        : ""
                    }
                    <h3 class="video-title">${
                      video.title || "タイトルなし"
                    }</h3>
                    <div class="video-meta">
                        <div class="video-id"><strong>ID:</strong> <code>${
                          video.id
                        }</code></div>
                        <div class="video-date">
                            <strong>投稿日:</strong> ${
                              video.formatted_create_time || "不明"
                            }
                        </div>
                    </div>
                    <div class="video-stats">
                        <div>
                            <div class="video-stat-number">${
                              video.view_count || 0
                            }</div>
                            <div class="video-stat-label">再生数</div>
                        </div>
                        <div>
                            <div class="video-stat-number">${
                              video.like_count || 0
                            }</div>
                            <div class="video-stat-label">いいね</div>
                        </div>
                        <div>
                            <div class="video-stat-number">${
                              video.comment_count || 0
                            }</div>
                            <div class="video-stat-label">コメント</div>
                        </div>
                    </div>
                    <a href="/video/${
                      video.id
                    }" class="btn btn-small">詳細を見る</a>
                </div>
            `
    )
    .join("");

  videoGrid.innerHTML = videoCards;
}

/**
 * ページネーション表示を更新
 */
function updatePaginationDisplay() {
  PaginationManager.updatePaginationDisplay();
}

/**
 * ヘッダーのアクティブ状態を更新
 * @param {string} openId - アクティブにするユーザーのOpen ID
 */
function updateHeaderActiveState(openId) {
  // すべてのユーザーアイテムからactiveクラスを削除
  document.querySelectorAll(".user-item").forEach((item) => {
    item.classList.remove("active");
  });

  // 指定されたユーザーアイテムにactiveクラスを追加
  const activeItem = document.querySelector(`[data-open-id="${openId}"]`);
  if (activeItem) {
    activeItem.classList.add("active");
  }
}

/**
 * ローディングオーバーレイを表示
 */
function showLoading() {
  const overlay = document.getElementById("loading-overlay");
  if (overlay) {
    overlay.style.display = "flex";
  }
}

/**
 * ローディングオーバーレイを非表示
 */
function hideLoading() {
  const overlay = document.getElementById("loading-overlay");
  if (overlay) {
    overlay.style.display = "none";
  }
}

/**
 * ページ読み込み時の初期化処理
 */
document.addEventListener("DOMContentLoaded", function () {
  // 初期データでページネーションを設定
  const videoGrid = document.getElementById("video-grid");
  if (videoGrid && videoGrid.children.length > 0) {
    // 既存の動画カードからデータを抽出
    const videoCards = Array.from(videoGrid.querySelectorAll(".video-card"));
    const videos = videoCards.map((card) => {
      const title =
        card.querySelector(".video-title")?.textContent || "タイトルなし";
      const id = card.querySelector(".video-id code")?.textContent || "";
      const date =
        card
          .querySelector(".video-date")
          ?.textContent.replace("投稿日:", "")
          .trim() || "";
      const viewCount = parseInt(
        card.querySelector(".video-stats .video-stat-number")?.textContent ||
          "0"
      );
      const likeCount = parseInt(
        card.querySelectorAll(".video-stats .video-stat-number")[1]
          ?.textContent || "0"
      );
      const commentCount = parseInt(
        card.querySelectorAll(".video-stats .video-stat-number")[2]
          ?.textContent || "0"
      );
      const imageUrl = card.querySelector(".video-cover")?.src || "";

      return {
        id: id,
        title: title,
        formatted_create_time: date,
        view_count: viewCount,
        like_count: likeCount,
        comment_count: commentCount,
        best_image_url: imageUrl,
      };
    });

    // ページネーションを初期化
    PaginationManager.init(videos);
    PaginationManager.updateDisplay();
  }
});
