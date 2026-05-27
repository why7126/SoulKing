const state = {
  songs: [],
  playlists: [],
  selectedSongId: null,
  selectedPlaylistId: null,
  queue: [],
  currentIndex: -1,
  playMode: "list-loop",
};

const els = {
  scanBtn: document.querySelector("#scanBtn"),
  searchBtn: document.querySelector("#searchBtn"),
  keywordInput: document.querySelector("#keywordInput"),
  formatSelect: document.querySelector("#formatSelect"),
  songList: document.querySelector("#songList"),
  playlistList: document.querySelector("#playlistList"),
  createPlaylistBtn: document.querySelector("#createPlaylistBtn"),
  playlistTarget: document.querySelector("#playlistTarget"),
  addToPlaylistBtn: document.querySelector("#addToPlaylistBtn"),
  detailEmpty: document.querySelector("#detailEmpty"),
  detailBody: document.querySelector("#detailBody"),
  detailTitle: document.querySelector("#detailTitle"),
  detailMeta: document.querySelector("#detailMeta"),
  variantList: document.querySelector("#variantList"),
  audioPlayer: document.querySelector("#audioPlayer"),
  nowPlaying: document.querySelector("#nowPlaying"),
  prevBtn: document.querySelector("#prevBtn"),
  nextBtn: document.querySelector("#nextBtn"),
  playModeSelect: document.querySelector("#playModeSelect"),
  toastContainer: document.querySelector("#toastContainer"),
  modalOverlay: document.querySelector("#modalOverlay"),
  modalTitle: document.querySelector("#modalTitle"),
  modalMessage: document.querySelector("#modalMessage"),
  modalInputWrap: document.querySelector("#modalInputWrap"),
  modalInput: document.querySelector("#modalInput"),
  modalCloseBtn: document.querySelector("#modalCloseBtn"),
  modalCancelBtn: document.querySelector("#modalCancelBtn"),
  modalConfirmBtn: document.querySelector("#modalConfirmBtn"),
};

const modalState = {
  resolver: null,
};

let appAudioPlayGeneration = 0;

const WEB_PLAYABLE_AUDIO_FORMATS = new Set(["mp3", "m4a", "aac", "ogg", "wav", "flac"]);

function normalizeAudioFmtApp(f) {
  return String(f || "").toLowerCase().replace(/^\./, "").trim();
}

function songHasWebPlayableAudioApp(song) {
  if (!song) return false;
  const fm = (song.formats || []).map((x) => normalizeAudioFmtApp(x)).filter(Boolean);
  if (fm.length) return fm.some((x) => WEB_PLAYABLE_AUDIO_FORMATS.has(x));
  if (song.file_format) return WEB_PLAYABLE_AUDIO_FORMATS.has(normalizeAudioFmtApp(song.file_format));
  return false;
}

function syncAddToPlaylistButton() {
  if (!els.addToPlaylistBtn) return;
  const song = state.songs.find((s) => s.id === state.selectedSongId);
  const ok = !!(song && songHasWebPlayableAudioApp(song));
  els.addToPlaylistBtn.disabled = !ok;
  els.addToPlaylistBtn.title = ok ? "加入歌单" : "该歌曲仅含 APE 等格式，不支持加入歌单";
  els.addToPlaylistBtn.classList.toggle("hidden", !ok);
}

function resolveMediaSrc(pathOrUrl) {
  if (pathOrUrl == null || pathOrUrl === "") return pathOrUrl;
  const s = String(pathOrUrl);
  if (s.startsWith("http://") || s.startsWith("https://") || s.startsWith("blob:")) return s;
  const base = typeof window !== "undefined" && window.location?.origin ? window.location.origin : "";
  return s.startsWith("/") ? `${base}${s}` : `${base}/${s}`;
}

async function request(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json();
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  els.toastContainer.appendChild(toast);
  window.setTimeout(() => {
    toast.remove();
  }, 2800);
}

function closeModal(result = null) {
  els.modalOverlay.classList.add("hidden");
  const resolver = modalState.resolver;
  modalState.resolver = null;
  if (resolver) resolver(result);
}

function openModal({ title, message, withInput = false, confirmText = "确定", cancelText = "取消", defaultValue = "" }) {
  els.modalTitle.textContent = title;
  els.modalMessage.textContent = message;
  els.modalConfirmBtn.textContent = confirmText;
  els.modalCancelBtn.textContent = cancelText;
  els.modalInputWrap.classList.toggle("hidden", !withInput);
  els.modalInput.value = defaultValue;
  els.modalOverlay.classList.remove("hidden");
  if (withInput) {
    window.setTimeout(() => els.modalInput.focus(), 0);
  }

  return new Promise((resolve) => {
    modalState.resolver = resolve;
  });
}

function fmtDuration(ms) {
  if (!ms) return "--:--";
  const sec = Math.floor(ms / 1000);
  return `${String(Math.floor(sec / 60)).padStart(2, "0")}:${String(sec % 60).padStart(2, "0")}`;
}

function fmtSize(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let n = bytes;
  let idx = 0;
  while (n >= 1024 && idx < units.length - 1) {
    n /= 1024;
    idx += 1;
  }
  return `${n.toFixed(idx === 0 ? 0 : 1)} ${units[idx]}`;
}

function buildSongMarkup(song) {
  return `
    <div class="song-main">
      <p class="song-title">${song.title}</p>
      <p class="song-meta">${song.artist || "Unknown Artist"} · ${song.album || "Unknown Album"} · ${fmtDuration(song.duration_ms)}</p>
    </div>
    <div class="tag-list">
      ${(song.formats || []).map((fmt) => `<span class="tag">${fmt.toUpperCase()}</span>`).join("")}
    </div>
  `;
}

function renderSongList() {
  els.songList.innerHTML = "";
  if (!state.songs.length) {
    els.songList.innerHTML = '<p class="empty">暂无歌曲</p>';
    return;
  }

  state.songs.forEach((song) => {
    const item = document.createElement("article");
    item.className = "song-item";
    if (song.id === state.selectedSongId) item.classList.add("active");
    item.innerHTML = buildSongMarkup(song);
    item.addEventListener("click", () => openSongDetail(song.id));
    els.songList.appendChild(item);
  });
  syncAddToPlaylistButton();
}

function renderPlaylists() {
  els.playlistList.innerHTML = "";
  els.playlistTarget.innerHTML = '<option value="">选择歌单</option>';

  const allItem = document.createElement("article");
  allItem.className = "playlist-item";
  if (!state.selectedPlaylistId) allItem.classList.add("active");
  allItem.innerHTML = '<strong>全部歌曲</strong><p class="song-meta">完整音乐库</p>';
  allItem.addEventListener("click", async () => {
    state.selectedPlaylistId = null;
    await loadSongs();
    renderPlaylists();
  });
  els.playlistList.appendChild(allItem);

  state.playlists.forEach((playlist) => {
    const item = document.createElement("article");
    item.className = "playlist-item";
    if (playlist.id === state.selectedPlaylistId) item.classList.add("active");
    item.innerHTML = `<strong>${playlist.name}</strong><p class="song-meta">${playlist.song_count} 首歌曲</p>`;
    item.addEventListener("click", async () => {
      state.selectedPlaylistId = playlist.id;
      await loadPlaylistSongs(playlist.id);
      renderPlaylists();
    });
    els.playlistList.appendChild(item);

    const option = document.createElement("option");
    option.value = playlist.id;
    option.textContent = playlist.name;
    els.playlistTarget.appendChild(option);
  });
}

async function loadPlaylists() {
  state.playlists = await request("/playlists");
  renderPlaylists();
}

async function loadSongs() {
  const params = new URLSearchParams();
  const keyword = els.keywordInput.value.trim();
  const format = els.formatSelect.value;
  if (keyword) params.set("keyword", keyword);
  if (format) params.set("format", format);
  const page = await request(`/songs?${params.toString()}`);
  state.songs = page.items || [];
  syncQueue();
  renderSongList();
}

async function loadPlaylistSongs(playlistId) {
  const detail = await request(`/playlists/${playlistId}`);
  state.songs = detail.songs;
  syncQueue();
  renderSongList();
}

function clearDetail() {
  els.detailBody.classList.add("hidden");
  els.detailEmpty.classList.remove("hidden");
  els.variantList.innerHTML = "";
}

function syncQueue() {
  state.queue = [...state.songs];
  if (!state.queue.length) {
    state.currentIndex = -1;
    return;
  }
  if (state.selectedSongId) {
    state.currentIndex = state.queue.findIndex((song) => song.id === state.selectedSongId);
  }
}

async function playSongAt(index, failureAttempt = 0) {
  if (!state.queue.length || index < 0 || index >= state.queue.length) return;
  if (state.queue.length && failureAttempt >= state.queue.length) {
    showToast("列表中的歌曲均无法播放", "error");
    return;
  }
  const song = state.queue[index];
  if (!songHasWebPlayableAudioApp(song)) {
    state.currentIndex = index;
    state.selectedSongId = song.id;
    renderSongList();
    const idx = nextIndexAfterPlaybackFailure();
    if (idx >= 0 && state.queue[idx] && songHasWebPlayableAudioApp(state.queue[idx])) {
      showToast("当前曲目无可播格式，已跳过", "warning");
      playSongAt(idx, failureAttempt + 1).catch(() => {});
    } else {
      let fallback = -1;
      const len = state.queue.length;
      for (let step = 1; step <= len; step++) {
        const i = (index + step) % len;
        if (songHasWebPlayableAudioApp(state.queue[i])) {
          fallback = i;
          break;
        }
      }
      if (fallback >= 0) {
        showToast("当前曲目无可播格式，已跳过", "warning");
        playSongAt(fallback, failureAttempt + 1).catch(() => {});
      } else {
        showToast("列表中的歌曲均无法播放", "error");
      }
    }
    return;
  }
  state.currentIndex = index;
  state.selectedSongId = song.id;
  renderSongList();
  const playInfo = await request(`/songs/${song.id}/play`);
  const audio = els.audioPlayer;
  const streamSrc = resolveMediaSrc(playInfo.stream_url);
  appAudioPlayGeneration += 1;
  const gen = appAudioPlayGeneration;

  const skipToNext = (message) => {
    if (gen !== appAudioPlayGeneration) return;
    if (state.playMode === "single-loop") {
      showToast("当前曲目无法播放", "error");
      return;
    }
    const idx = nextIndexAfterPlaybackFailure();
    if (idx >= 0 && state.queue[idx]) {
      showToast(message || "当前曲目无法播放，已跳过", "warning");
      playSongAt(idx, failureAttempt + 1).catch(() => {});
    } else {
      showToast("播放失败", "error");
    }
  };

  const onErr = () => {
    audio.removeEventListener("error", onErr);
    if (gen !== appAudioPlayGeneration) return;
    skipToNext("当前曲目无法播放，已跳过");
  };
  audio.addEventListener("error", onErr, { once: true });

  audio.src = streamSrc;
  els.nowPlaying.textContent = `${song.title} · ${playInfo.selected_format.toUpperCase()}`;
  try {
    await audio.play();
  } catch (_err) {
    audio.removeEventListener("error", onErr);
    if (gen !== appAudioPlayGeneration) return;
    skipToNext("当前曲目无法播放，已跳过");
  }
}

function nextIndex() {
  if (!state.queue.length) return -1;
  if (state.playMode === "single-loop") return state.currentIndex;
  if (state.playMode === "shuffle") return Math.floor(Math.random() * state.queue.length);
  if (state.currentIndex < state.queue.length - 1) return state.currentIndex + 1;
  if (state.playMode === "list-loop") return 0;
  // sequence：最后一首后不循环
  return -1;
}

/** 非单曲模式下跳过失败曲目；若下一索引仍为当前曲则顺序进一位 */
function nextIndexAfterPlaybackFailure() {
  const len = state.queue.length;
  if (len <= 1) return -1;
  const normal = nextIndex();
  if (normal !== state.currentIndex) return normal;
  return (state.currentIndex + 1) % len;
}

function prevIndex() {
  if (!state.queue.length) return -1;
  if (state.playMode === "single-loop") return state.currentIndex;
  if (state.playMode === "shuffle") return Math.floor(Math.random() * state.queue.length);
  if (state.currentIndex > 0) return state.currentIndex - 1;
  if (state.playMode === "list-loop") return state.queue.length - 1;
  return -1;
}

async function openSongDetail(songId) {
  state.selectedSongId = songId;
  state.currentIndex = state.queue.findIndex((song) => song.id === songId);
  renderSongList();

  const detail = await request(`/songs/${songId}`);
  syncAddToPlaylistButton();
  els.detailEmpty.classList.add("hidden");
  els.detailBody.classList.remove("hidden");
  els.detailTitle.textContent = detail.title;
  els.detailMeta.textContent = `${detail.artist || "Unknown Artist"} · ${detail.album || "Unknown Album"} · ${fmtDuration(detail.duration_ms)}`;
  els.variantList.innerHTML = "";

  detail.files.forEach((file) => {
    const card = document.createElement("article");
    card.className = "variant-item";
    card.innerHTML = `
      <strong>${file.format.toUpperCase()}</strong>
      <p class="variant-meta">${file.bitrate ? `${file.bitrate} kbps` : "-"} · ${file.sample_rate ? `${file.sample_rate} Hz` : "-"} · ${file.channels ? `${file.channels}ch` : "-"} · ${fmtSize(file.file_size)}</p>
      <div class="variant-actions">
        ${file.is_playable_web ? '<button class="btn btn-primary" data-role="play">试听</button>' : ""}
        <button class="btn" data-role="download">下载</button>
      </div>
    `;

    const playVariantBtn = card.querySelector('[data-role="play"]');
    if (playVariantBtn) {
      playVariantBtn.addEventListener("click", async () => {
        try {
          els.audioPlayer.src = resolveMediaSrc(`/song-files/${file.id}/stream`);
          els.nowPlaying.textContent = `${detail.title} · ${file.format.toUpperCase()}`;
          await els.audioPlayer.play();
        } catch (err) {
          showToast(`试听失败: ${err.message}`, "error");
        }
      });
    }

    card.querySelector('[data-role="download"]').addEventListener("click", async () => {
      try {
        const payload = await request(`/song-files/${file.id}/download`);
        window.open(payload.url, "_blank", "noopener");
      } catch (err) {
        showToast(`下载失败: ${err.message}`, "error");
      }
    });

    els.variantList.appendChild(card);
  });
}

async function createPlaylist() {
  const name = await openModal({
    title: "新建歌单",
    message: "请输入新的歌单名称。",
    withInput: true,
    confirmText: "创建",
  });
  if (!name || !name.trim()) return;
  await request("/playlists", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name.trim() }),
  });
  await loadPlaylists();
  showToast("歌单已创建", "success");
}

async function addSelectedSongToPlaylist() {
  const playlistId = els.playlistTarget.value;
  if (!playlistId) {
    showToast("请先选择歌单", "error");
    return;
  }
  if (!state.selectedSongId) {
    showToast("请先选择歌曲", "error");
    return;
  }
  await request(`/playlists/${playlistId}/items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ song_id: state.selectedSongId }),
  });
  await loadPlaylists();
  showToast("已加入歌单", "success");
}

async function runScan() {
  els.scanBtn.disabled = true;
  els.scanBtn.textContent = "扫描中...";
  try {
    const result = await request("/libraries/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    if (state.selectedPlaylistId) {
      await loadPlaylistSongs(state.selectedPlaylistId);
    } else {
      await loadSongs();
    }
    await loadPlaylists();
    showToast(`扫描完成: 扫描 ${result.scanned_count}，新增 ${result.added_count}，跳过 ${result.skipped_count}`, "success");
    if (result.skipped_count > 0 && Array.isArray(result.skipped_details) && result.skipped_details.length) {
      const lines = result.skipped_details.map((d) => `${d.path}: ${d.reason || "未知原因"}`);
      window.alert(`以下文件已跳过：\n\n${lines.join("\n")}`);
    }
  } catch (err) {
    showToast(`扫描失败: ${err.message}`, "error");
  } finally {
    els.scanBtn.disabled = false;
    els.scanBtn.textContent = "扫描音乐目录";
  }
}

els.searchBtn.addEventListener("click", () => loadSongs().catch((err) => showToast(`查询失败: ${err.message}`, "error")));
els.scanBtn.addEventListener("click", () => runScan().catch((err) => showToast(`扫描失败: ${err.message}`, "error")));
els.createPlaylistBtn.addEventListener("click", () => createPlaylist().catch((err) => showToast(`创建歌单失败: ${err.message}`, "error")));
els.addToPlaylistBtn.addEventListener("click", () => addSelectedSongToPlaylist().catch((err) => showToast(`加入歌单失败: ${err.message}`, "error")));
els.prevBtn.addEventListener("click", () => {
  const idx = prevIndex();
  if (idx >= 0) playSongAt(idx).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
});
els.nextBtn.addEventListener("click", () => {
  const idx = nextIndex();
  if (idx >= 0) playSongAt(idx).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
});
els.playModeSelect.addEventListener("change", (event) => {
  state.playMode = event.target.value;
});
els.audioPlayer.addEventListener("ended", () => {
  const idx = nextIndex();
  if (idx >= 0) playSongAt(idx).catch(() => {});
});
els.keywordInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") loadSongs().catch((err) => showToast(`查询失败: ${err.message}`, "error"));
});

els.modalCloseBtn.addEventListener("click", () => closeModal(null));
els.modalCancelBtn.addEventListener("click", () => closeModal(null));
els.modalConfirmBtn.addEventListener("click", () => {
  const value = els.modalInputWrap.classList.contains("hidden") ? true : els.modalInput.value;
  closeModal(value);
});
els.modalOverlay.addEventListener("click", (event) => {
  if (event.target === els.modalOverlay) closeModal(null);
});
els.modalInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") closeModal(els.modalInput.value);
});

Promise.all([loadSongs(), loadPlaylists()]).catch((err) => {
  els.songList.innerHTML = `<p class="empty">加载失败: ${err.message}</p>`;
});
