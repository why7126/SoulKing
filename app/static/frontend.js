const state = {
  songs: [],
  playlists: [],
  filters: null,
  librarySongCount: 0,
  selectedPlaylistId: null,
  queue: [],
  currentIndex: -1,
  playMode: "list-loop",
  draggingPlaylistId: null,
};

const els = {
  keywordInput: document.querySelector("#keywordInput"),
  formatSelect: document.querySelector("#formatSelect"),
  tagSelect: document.querySelector("#tagSelect"),
  languageSelect: document.querySelector("#languageSelect"),
  songList: document.querySelector("#songList"),
  playlistList: document.querySelector("#playlistList"),
  createPlaylistBtn: document.querySelector("#createPlaylistBtn"),
  audioPlayer: document.querySelector("#audioPlayer"),
  nowPlaying: document.querySelector("#nowPlaying"),
  prevBtn: document.querySelector("#prevBtn"),
  nextBtn: document.querySelector("#nextBtn"),
  playPlaylistBtn: document.querySelector("#playPlaylistBtn"),
  playModeSelect: document.querySelector("#playModeSelect"),
  toastContainer: document.querySelector("#toastContainer"),
  modalOverlay: document.querySelector("#modalOverlay"),
  modalTitle: document.querySelector("#modalTitle"),
  modalMessage: document.querySelector("#modalMessage"),
  modalInputWrap: document.querySelector("#modalInputWrap"),
  modalInput: document.querySelector("#modalInput"),
  modalSelectWrap: document.querySelector("#modalSelectWrap"),
  modalSelect: document.querySelector("#modalSelect"),
  modalCloseBtn: document.querySelector("#modalCloseBtn"),
  modalCancelBtn: document.querySelector("#modalCancelBtn"),
  modalConfirmBtn: document.querySelector("#modalConfirmBtn"),
  goAdminBtn: document.querySelector("#goAdminBtn"),
};

const modalState = { resolver: null };

function getApiUrl(path) {
  const base = typeof window !== "undefined" && window.location && window.location.origin ? window.location.origin : "";
  return path.startsWith("http") ? path : `${base}${path}`;
}

async function request(path, options = {}) {
  const url = getApiUrl(path);
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `Request failed: ${res.status}`);
    }
    if (res.status === 204) return null;
    return res.json();
  } catch (err) {
    if (err.name === "TypeError" && (err.message === "Failed to fetch" || err.message.includes("fetch"))) {
      throw new Error("无法连接服务器，请确认后端服务已启动并刷新页面");
    }
    throw err;
  }
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  els.toastContainer.appendChild(toast);
  window.setTimeout(() => toast.remove(), 2800);
}

function closeModal(result = null) {
  els.modalOverlay.classList.add("hidden");
  const resolver = modalState.resolver;
  modalState.resolver = null;
  if (resolver) resolver(result);
}

function openModal({ title, message, withInput = false, withSelect = false, selectOptions = [], confirmText = "确定", cancelText = "取消", defaultValue = "" }) {
  els.modalTitle.textContent = title;
  els.modalMessage.textContent = message;
  els.modalConfirmBtn.textContent = confirmText;
  els.modalCancelBtn.textContent = cancelText;
  els.modalInputWrap.classList.toggle("hidden", !withInput);
  els.modalSelectWrap.classList.toggle("hidden", !withSelect);
  els.modalInput.value = defaultValue;
  if (withSelect) {
    els.modalSelect.innerHTML = selectOptions.map((option) => `<option value="${option.value}">${option.label}</option>`).join("");
    if (defaultValue) els.modalSelect.value = defaultValue;
  }
  els.modalOverlay.classList.remove("hidden");
  if (withInput) window.setTimeout(() => els.modalInput.focus(), 0);
  if (withSelect) window.setTimeout(() => els.modalSelect.focus(), 0);
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
  if (!bytes) return "0 MB";
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function renderFilterOptions() {
  els.formatSelect.innerHTML = ['<option value="">全部格式</option>', ...((state.filters?.formats || []).map((v) => `<option value="${v}">${v.toUpperCase()}</option>`))].join("");
  els.tagSelect.innerHTML = ['<option value="">全部标签</option>', ...((state.filters?.tags || []).map((tag) => `<option value="${tag.id}">${tag.name}</option>`))].join("");
  els.languageSelect.innerHTML = ['<option value="">全部语言</option>', ...((state.filters?.languages || []).map((lang) => `<option value="${lang.name}">${lang.name}</option>`))].join("");
}

async function loadFilterOptions() {
  state.filters = await request("/admin/filter-options");
  renderFilterOptions();
}

async function loadLibraryStats() {
  const stats = await request("/library/stats");
  state.librarySongCount = stats.song_count || 0;
}

function syncQueue() {
  state.queue = [...state.songs];
  if (state.currentIndex >= state.queue.length) state.currentIndex = state.queue.length - 1;
}

async function loadSongs() {
  const params = new URLSearchParams();
  const keyword = els.keywordInput.value.trim();
  if (keyword) params.set("keyword", keyword);
  if (els.formatSelect.value) params.append("formats", els.formatSelect.value);
  if (els.tagSelect.value) params.append("tag_ids", els.tagSelect.value);
  if (els.languageSelect.value) params.append("languages", els.languageSelect.value);

  if (state.selectedPlaylistId) {
    const detail = await request(`/playlists/${state.selectedPlaylistId}`);
    let songs = detail.songs;
    if (keyword) {
      const kw = keyword.toLowerCase();
      songs = songs.filter((song) => [song.title, song.artist, song.album].some((v) => (v || "").toLowerCase().includes(kw)));
    }
    if (els.formatSelect.value) songs = songs.filter((song) => (song.formats || []).includes(els.formatSelect.value));
    if (els.tagSelect.value) {
      const tag = state.filters.tags.find((item) => String(item.id) === els.tagSelect.value)?.name;
      songs = songs.filter((song) => (song.tags || []).includes(tag));
    }
    if (els.languageSelect.value) songs = songs.filter((song) => song.language === els.languageSelect.value);
    state.songs = songs;
  } else {
    params.set("limit", "500");
    state.songs = await request(`/songs?${params.toString()}`);
  }
  syncQueue();
  renderSongList();
}

async function loadPlaylists() {
  state.playlists = await request("/playlists");
  renderPlaylists();
}

function playlistCard(playlist, isActive) {
  return `
    <div class="playlist-item-inner ${isActive ? "active" : ""}">
      ${playlist.isAll ? "" : '<span class="drag-handle" title="拖拽排序">⋮</span>'}
      <div class="playlist-meta">
        <strong>${playlist.name}</strong>
        <p class="song-meta">${playlist.song_count || 0} 首歌曲</p>
      </div>
      <div class="playlist-actions-inline">
        <button class="btn btn-mini icon-btn" data-role="play" title="播放歌单" aria-label="播放歌单">▶</button>
        ${playlist.isAll ? "" : '<div class="playlist-more"><button class="btn btn-mini icon-btn" data-role="more" title="更多" aria-label="更多">⋯</button><div class="playlist-more-menu hidden" data-role="menu"><button class="btn btn-mini menu-btn" data-role="rename">✎ 编辑</button><button class="btn btn-mini menu-btn danger-text" data-role="delete">🗑 删除</button></div></div>'}
      </div>
    </div>
  `;
}

function renderPlaylists() {
  els.playlistList.innerHTML = "";
  const allPlaylist = { id: null, name: "全部歌曲", song_count: state.librarySongCount, isAll: true };
  const items = [allPlaylist, ...state.playlists.map((p) => ({ ...p, isAll: false }))];
  items.forEach((playlist) => {
    const item = document.createElement("article");
    item.className = "playlist-item";
    const isActive = playlist.id === state.selectedPlaylistId || (!playlist.id && state.selectedPlaylistId === null);
    if (isActive) item.classList.add("active");
    if (playlist.isAll) item.classList.add("all-songs-item");
    item.innerHTML = playlistCard(playlist, isActive);
    if (!playlist.isAll) {
      item.draggable = true;
      item.addEventListener("dragstart", () => { state.draggingPlaylistId = playlist.id; item.classList.add("dragging"); });
      item.addEventListener("dragend", () => {
        state.draggingPlaylistId = null;
        item.classList.remove("dragging");
        els.playlistList.querySelectorAll('.playlist-item').forEach((node) => node.classList.remove("drop-target"));
      });
      item.addEventListener("dragover", (e) => {
        e.preventDefault();
        els.playlistList.querySelectorAll('.playlist-item').forEach((node) => node.classList.remove("drop-target"));
        item.classList.add("drop-target");
      });
      item.addEventListener("dragleave", () => {
        item.classList.remove("drop-target");
      });
      item.addEventListener("drop", async (e) => {
        e.preventDefault();
        item.classList.remove("drop-target");
        if (!state.draggingPlaylistId || state.draggingPlaylistId === playlist.id) return;
        const ids = state.playlists.map((p) => p.id);
        const from = ids.indexOf(state.draggingPlaylistId);
        const to = ids.indexOf(playlist.id);
        const [moved] = ids.splice(from, 1);
        ids.splice(to, 0, moved);
        await request("/playlists-reorder", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ playlist_ids: ids }) });
        await loadPlaylists();
        showToast("排序已保存", "success");
      });
    } else {
      item.draggable = false;
    }
    item.addEventListener("click", async (event) => {
      if (event.target.closest("[data-role]")) return;
      state.selectedPlaylistId = playlist.id;
      await loadSongs();
      renderPlaylists();
    });
    item.querySelector('[data-role="play"]').addEventListener("click", async (event) => {
      event.stopPropagation();
      state.selectedPlaylistId = playlist.id;
      await loadSongs();
      renderPlaylists();
      playCurrentPlaylist();
    });
    if (!playlist.isAll) {
      const moreBtn = item.querySelector('[data-role="more"]');
      const menu = item.querySelector('[data-role="menu"]');
      moreBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        els.playlistList.querySelectorAll('.playlist-more-menu').forEach((node) => {
          if (node !== menu) node.classList.add("hidden");
        });
        menu.classList.toggle("hidden");
      });
      item.querySelector('[data-role="rename"]').addEventListener("click", async (event) => {
        event.stopPropagation();
        menu.classList.add("hidden");
        const name = await openModal({ title: "修改歌单", message: "请输入新的歌单名称。", withInput: true, confirmText: "保存", defaultValue: playlist.name });
        if (!name || !name.trim()) return;
        await request(`/playlists/${playlist.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: name.trim() }) });
        await loadPlaylists();
      });
      item.querySelector('[data-role="delete"]').addEventListener("click", async (event) => {
        event.stopPropagation();
        menu.classList.add("hidden");
        const ok = await openModal({ title: "删除歌单", message: `确认删除歌单「${playlist.name}」吗？`, confirmText: "删除" });
        if (!ok) return;
        await request(`/playlists/${playlist.id}`, { method: "DELETE" });
        if (state.selectedPlaylistId === playlist.id) state.selectedPlaylistId = null;
        await Promise.all([loadPlaylists(), loadSongs()]);
      });
    }
    els.playlistList.appendChild(item);
  });
}

async function playSong(songId, preferredFormat = "") {
  const url = preferredFormat ? `/songs/${songId}/play?preferred_format=${preferredFormat}` : `/songs/${songId}/play`;
  const playInfo = await request(url);
  const song = state.songs.find((item) => item.id === songId);
  state.currentIndex = state.queue.findIndex((item) => item.id === songId);
  renderSongList();
  els.audioPlayer.src = playInfo.stream_url;
  els.nowPlaying.textContent = `${song?.title || "未知歌曲"} · ${playInfo.selected_format.toUpperCase()}`;
  await els.audioPlayer.play();
}

function nextIndex() {
  if (!state.queue.length) return -1;
  if (state.playMode === "single-loop") return state.currentIndex;
  if (state.playMode === "shuffle") return Math.floor(Math.random() * state.queue.length);
  if (state.currentIndex < state.queue.length - 1) return state.currentIndex + 1;
  if (state.playMode === "list-loop") return 0;
  return -1;
}

function prevIndex() {
  if (!state.queue.length) return -1;
  if (state.playMode === "single-loop") return state.currentIndex;
  if (state.playMode === "shuffle") return Math.floor(Math.random() * state.queue.length);
  if (state.currentIndex > 0) return state.currentIndex - 1;
  if (state.playMode === "list-loop") return state.queue.length - 1;
  return -1;
}

function playCurrentPlaylist() {
  if (!state.queue.length) return showToast("当前歌单暂无歌曲", "error");
  playSong(state.queue[0].id).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
}

async function addSongToPlaylist(songId) {
  if (!state.playlists.length) return showToast("请先创建歌单", "error");
  const choice = await openModal({
    title: "加入歌单",
    message: "请选择要加入的歌单。",
    withSelect: true,
    selectOptions: state.playlists.map((p) => ({ value: String(p.id), label: p.name })),
    confirmText: "加入",
  });
  if (!choice) return;
  const playlist = state.playlists.find((p) => String(p.id) === String(choice).trim());
  if (!playlist) return showToast("歌单编号无效", "error");
  await request(`/playlists/${playlist.id}/items`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ song_id: songId }) });
  await loadPlaylists();
  showToast("已加入歌单", "success");
}

async function removeSongFromCurrentPlaylist(songId) {
  if (!state.selectedPlaylistId) return;
  const ok = await openModal({ title: "移出歌单", message: "确认将该歌曲从当前歌单移除吗？", confirmText: "移除" });
  if (!ok) return;
  await request(`/playlists/${state.selectedPlaylistId}/items/${songId}`, { method: "DELETE" });
  await loadSongs();
  await loadPlaylists();
}

function songActionsMarkup(song) {
  const removable = state.selectedPlaylistId !== null;
  const infoTags = [
    ...((song.formats || []).map((fmt) => ({ label: fmt.toUpperCase(), kind: "format" }))),
    ...(song.language ? [{ label: song.language, kind: "language" }] : []),
    ...(song.genre ? [{ label: song.genre, kind: "genre" }] : []),
    ...((song.tags || []).map((tag) => ({ label: tag, kind: "tag" }))),
  ];
  return `
    <div class="song-main">
      <div class="song-title-row">
        <p class="song-title">${song.title}</p>
        <div class="tag-list song-info-tags">
        ${infoTags.map((item) => `<span class="tag tag-${item.kind}">${item.label}</span>`).join("") || '<span class="tag">未分类</span>'}
        </div>
      </div>
      <p class="song-meta">原唱：${song.lead_artist || "无"}</p>
      <p class="song-meta">作词：${(song.lyricists || []).join(" / ") || "无"} · 作曲：${(song.composers || []).join(" / ") || "无"}</p>
      <p class="song-meta"><span title="专辑">${song.album || "Unknown Album"}</span> · <span title="时长">${fmtDuration(song.duration_ms)}</span>${song.release_date ? ` · <span title="发行日期">${song.release_date}</span>` : ""}</p>
    </div>
    <div class="song-row-actions">
      <button class="btn btn-mini icon-btn" data-role="play" title="试听" aria-label="试听">▶</button>
      <button class="btn btn-mini icon-btn" data-role="add" title="加入歌单" aria-label="加入歌单">＋</button>
      <button class="btn btn-mini icon-btn" data-role="download" title="下载" aria-label="下载">↓</button>
      ${removable ? '<button class="btn btn-mini icon-btn danger-text" data-role="delete" title="删除" aria-label="删除">🗑</button>' : ""}
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
    item.className = "song-item front-song-item";
    if (state.currentIndex >= 0 && state.queue[state.currentIndex]?.id === song.id) {
      item.classList.add("active");
    }
    item.innerHTML = songActionsMarkup(song);
    item.addEventListener("dblclick", () => {
      playSong(song.id).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
    });
    item.querySelector('[data-role="add"]').addEventListener("click", (e) => {
      e.stopPropagation();
      addSongToPlaylist(song.id).catch((err) => showToast(`加入歌单失败: ${err.message}`, "error"));
    });
    item.querySelector('[data-role="play"]').addEventListener("click", (e) => {
      e.stopPropagation();
      playSong(song.id).catch((err) => showToast(`试听失败: ${err.message}`, "error"));
    });
    item.querySelector('[data-role="download"]').addEventListener("click", async (e) => {
      e.stopPropagation();
      try {
        const playInfo = await request(`/songs/${song.id}/play`);
        const link = document.createElement("a");
        link.href = playInfo.download_url;
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (err) {
        showToast(`下载失败: ${err.message}`, "error");
      }
    });
    const delBtn = item.querySelector('[data-role="delete"]');
    if (delBtn) {
      delBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        removeSongFromCurrentPlaylist(song.id).catch((err) => showToast(`删除失败: ${err.message}`, "error"));
      });
    }
    els.songList.appendChild(item);
  });
}

async function createPlaylist() {
  const name = await openModal({ title: "新建歌单", message: "请输入新的歌单名称。", withInput: true, confirmText: "创建" });
  if (!name || !name.trim()) return;
  await request("/playlists", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name.trim() }),
  });
  await loadPlaylists();
  showToast("歌单已创建", "success");
}

els.createPlaylistBtn.addEventListener("click", () => createPlaylist().catch((err) => showToast(`创建歌单失败: ${err.message}`, "error")));
els.prevBtn.addEventListener("click", () => {
  const idx = prevIndex();
  if (idx >= 0) playSong(state.queue[idx].id).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
});
els.nextBtn.addEventListener("click", () => {
  const idx = nextIndex();
  if (idx >= 0) playSong(state.queue[idx].id).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
});
els.playPlaylistBtn.addEventListener("click", playCurrentPlaylist);
els.playModeSelect.addEventListener("change", (event) => { state.playMode = event.target.value; });
els.audioPlayer.addEventListener("ended", () => {
  const idx = nextIndex();
  if (idx >= 0) playSong(state.queue[idx].id).catch(() => {});
});
els.keywordInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") loadSongs().catch((err) => showToast(`查询失败: ${err.message}`, "error"));
});
[els.formatSelect, els.tagSelect, els.languageSelect].forEach((el) => {
  el.addEventListener("change", () => loadSongs().catch((err) => showToast(`筛选失败: ${err.message}`, "error")));
});
els.modalCloseBtn.addEventListener("click", () => closeModal(null));
els.modalCancelBtn.addEventListener("click", () => closeModal(null));
els.modalConfirmBtn.addEventListener("click", () => {
  if (!els.modalInputWrap.classList.contains("hidden")) return closeModal(els.modalInput.value);
  if (!els.modalSelectWrap.classList.contains("hidden")) return closeModal(els.modalSelect.value);
  closeModal(true);
});
els.modalOverlay.addEventListener("click", (event) => { if (event.target === els.modalOverlay) closeModal(null); });
els.modalInput.addEventListener("keydown", (event) => { if (event.key === "Enter") closeModal(els.modalInput.value); });
els.modalSelect.addEventListener("keydown", (event) => { if (event.key === "Enter") closeModal(els.modalSelect.value); });
els.goAdminBtn.addEventListener("click", () => { window.location.href = "/admin"; });
document.addEventListener("click", () => {
  els.playlistList.querySelectorAll('.playlist-more-menu').forEach((node) => node.classList.add("hidden"));
});

async function initPage() {
  try {
    await loadFilterOptions();
    await loadLibraryStats();
    await loadPlaylists();
    await loadSongs();
  } catch (err) {
    els.songList.innerHTML = `<p class="empty">加载失败: ${err.message}</p>`;
    showToast(`前台初始化失败: ${err.message}`, "error");
  }
}

initPage();
