/**
 * ダッシュボードページ用JavaScript
 */

// SPA風のユーザー切り替え機能
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

// ダッシュボードコンテンツを更新
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
    const shareCount = document.getElementById("share-count");
    if (shareCount) {
      shareCount.textContent = user_info.total_share_count || 0;
    }

    const avgEngagementRate = document.getElementById("avg-engagement-rate");
    if (avgEngagementRate) {
      avgEngagementRate.textContent = user_info.avg_engagement_rate || 0;
    }
  }

  // 動画リストを更新
  if (videos) {
    updateVideoGrid(videos);
  }

  // ヘッダーのアクティブ状態を更新
  updateHeaderActiveState(user_info.open_id);
}

// 動画グリッドを更新
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

// ヘッダーのアクティブ状態を更新
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

// ローディング表示
function showLoading() {
  const overlay = document.getElementById("loading-overlay");
  if (overlay) {
    overlay.style.display = "flex";
  }
}

function hideLoading() {
  const overlay = document.getElementById("loading-overlay");
  if (overlay) {
    overlay.style.display = "none";
  }
}
