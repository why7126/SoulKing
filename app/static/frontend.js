import { applyAppVersion } from "./version.js";
import { findLyricLineAtTime, loadSongLyricsViaRequest, LYRIC_PLACEHOLDER } from "./lrc.js";
import {
  clearActiveSearchableSelectMenu,
  closeActiveSearchableSelectMenuOnOutsideClick,
  ensureSearchableSelect,
  filterDropdownSelectedRawValues,
  getActiveSearchableSelectMenu,
  refreshSearchableSelectOptions,
  syncSearchableSelectTrigger,
} from "./searchable-select.js";

const state = {
  songs: [],
  playlists: [],
  filters: null,
  librarySongCount: 0,
  selectedPlaylistId: null,
  /** 侧栏「音乐库」对应的曲目页 vs 「歌单」列表 / 详情 */
  mainNav: "library",
  /** 非空时表示处于歌单详情页（仍归属 mainNav === "playlists"） */
  playlistDetailId: null,
  playlistDetailAllSongs: [],
  playlistHubFilter: "",
  playlistSort: "updated",
  playlistViewGrid: true,
  selectedSongId: null,
  queue: [],
  currentIndex: -1,
  playMode: "list-loop",
  draggingPlaylistId: null,
  inspectorTab: "detail",
  songPage: 1,
  songPageSize: 20,
  songListTotal: 0,
  lyricLines: [],
  lyricSongId: null,
  lyricContent: "",
};

let frontAudioPlayGeneration = 0;
let lastPlayerLyricText = "";
const LYRICS_VISIBLE_STORAGE_KEY = "sk.player.lyricsVisible";

const els = {
  keywordInput: document.querySelector("#keywordInput"),
  frontKeywordClearBtn: document.querySelector("#frontKeywordClearBtn"),
  libraryKeywordInput: document.querySelector("#libraryKeywordInput"),
  libraryKeywordClearBtn: document.querySelector("#libraryKeywordClearBtn"),
  resetFrontFiltersBtn: document.querySelector("#resetFrontFiltersBtn"),
  frontToggleFilterBtn: document.querySelector("#frontToggleFilterBtn"),
  frontFilterSection: document.querySelector("#frontFilterSection"),
  filterLeadQuick: document.querySelector("#frontFilterLeadQuick"),
  filterLyricistQuick: document.querySelector("#frontFilterLyricistQuick"),
  filterComposerQuick: document.querySelector("#frontFilterComposerQuick"),
  formatSelect: document.querySelector("#formatSelect"),
  tagSelect: document.querySelector("#tagSelect"),
  languageSelect: document.querySelector("#languageSelect"),
  genreSelect: document.querySelector("#genreSelect"),
  songList: document.querySelector("#songList"),
  playlistDetailSongList: document.querySelector("#playlistDetailSongList"),
  createPlaylistBtn: document.querySelector("#createPlaylistBtn"),
  audioPlayer: document.querySelector("#audioPlayer"),
  prevBtn: document.querySelector("#prevBtn"),
  nextBtn: document.querySelector("#nextBtn"),
  playPlaylistBtn: document.querySelector("#playPlaylistBtn"),
  playModeSelect: document.querySelector("#playModeSelect"),
  playerPlayPauseBtn: document.querySelector("#playerPlayPauseBtn"),
  playerProgressTrack: document.querySelector("#playerProgressTrack"),
  playerProgressFill: document.querySelector("#playerProgressFill"),
  playerCurrentTime: document.querySelector("#playerCurrentTime"),
  playerDuration: document.querySelector("#playerDuration"),
  playerVolume: document.querySelector("#playerVolume"),
  playerBarTitle: document.querySelector("#playerBarTitle"),
  playerBarArtist: document.querySelector("#playerBarArtist"),
  playerNextHint: document.querySelector("#playerNextHint"),
  playerLyricLine: document.querySelector("#playerLyricLine"),
  playerLyricsToggleBtn: document.querySelector("#playerLyricsToggleBtn"),
  studioPlayer: document.querySelector(".studio-player"),
  playerThumb: document.querySelector("#playerThumb"),
  librarySongCount: document.querySelector("#librarySongCount"),
  sidebarSongCount: document.querySelector("#sidebarSongCount"),
  frontSongListTotalLabel: document.querySelector("#frontSongListTotalLabel"),
  frontPageInfoLabel: document.querySelector("#frontPageInfoLabel"),
  frontPageFirstBtn: document.querySelector("#frontPageFirstBtn"),
  frontPagePrevBtn: document.querySelector("#frontPagePrevBtn"),
  frontPageNextBtn: document.querySelector("#frontPageNextBtn"),
  frontPageLastBtn: document.querySelector("#frontPageLastBtn"),
  frontPageNumbers: document.querySelector("#frontPageNumbers"),
  frontPageSizeSelect: document.querySelector("#frontPageSizeSelect"),
  frontUserMenuBtn: document.querySelector("#frontUserMenuBtn"),
  frontUserMenu: document.querySelector("#frontUserMenu"),
  frontUserProfileBtn: document.querySelector("#frontUserProfileBtn"),
  frontUserPasswordBtn: document.querySelector("#frontUserPasswordBtn"),
  frontUserAdminBtn: document.querySelector("#frontUserAdminBtn"),
  frontUserLogoutBtn: document.querySelector("#frontUserLogoutBtn"),
  inspectorTitle: document.querySelector("#inspectorTitle"),
  inspectorArtist: document.querySelector("#inspectorArtist"),
  inspectorBody: document.querySelector("#inspectorBody"),
  inspectorEmpty: document.querySelector("#inspectorEmpty"),
  inspectorDetail: document.querySelector("#inspectorDetail"),
  inspectorPlayBtn: document.querySelector("#inspectorPlayBtn"),
  inspectorCover: document.querySelector("#inspectorCover"),
  inspectorCoverPh: document.querySelector("#inspectorCoverPh"),
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
  downloadFormatsOverlay: document.querySelector("#downloadFormatsOverlay"),
  downloadFormatsHint: document.querySelector("#downloadFormatsHint"),
  downloadFormatsList: document.querySelector("#downloadFormatsList"),
  downloadFormatsCloseBtn: document.querySelector("#downloadFormatsCloseBtn"),
  downloadFormatsCancelBtn: document.querySelector("#downloadFormatsCancelBtn"),
  downloadFormatsConfirmBtn: document.querySelector("#downloadFormatsConfirmBtn"),
};

const modalState = { resolver: null };

/** 浏览器可试听格式（与后端 is_playable_web 一致，不含 APE） */
const WEB_PLAYABLE_AUDIO_FORMATS = new Set(["mp3", "m4a", "aac", "ogg", "wav", "flac"]);

function normalizeAudioFmtList(f) {
  return String(f || "").toLowerCase().replace(/^\./, "").trim();
}

function songHasWebPlayableAudio(song) {
  if (!song) return false;
  const variants = song.file_variants || [];
  const fromV = variants.map((v) => normalizeAudioFmtList(v.format)).filter(Boolean);
  if (fromV.length) return fromV.some((x) => WEB_PLAYABLE_AUDIO_FORMATS.has(x));
  const fm = (song.formats || []).map((x) => normalizeAudioFmtList(x)).filter(Boolean);
  if (fm.length) return fm.some((x) => WEB_PLAYABLE_AUDIO_FORMATS.has(x));
  if (song.file_format) return WEB_PLAYABLE_AUDIO_FORMATS.has(normalizeAudioFmtList(song.file_format));
  return false;
}

function getApiUrl(path) {
  const base = typeof window !== "undefined" && window.location && window.location.origin ? window.location.origin : "";
  return path.startsWith("http") ? path : `${base}${path}`;
}

/** 供 <audio src> 使用，与 fetch 同源一致，减少部分浏览器对相对路径解码的差异 */
function resolveMediaSrc(pathOrUrl) {
  if (pathOrUrl == null || pathOrUrl === "") return pathOrUrl;
  const s = String(pathOrUrl);
  if (s.startsWith("http://") || s.startsWith("https://") || s.startsWith("blob:")) return s;
  return getApiUrl(s.startsWith("/") ? s : `/${s}`);
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

function wireSearchFieldClear(inputEl, clearBtnEl, onCleared, onInputSync) {
  if (!inputEl || !clearBtnEl) return;
  const sync = () => {
    clearBtnEl.classList.toggle("hidden", !inputEl.value.trim());
    if (typeof onInputSync === "function") onInputSync();
  };
  inputEl.addEventListener("input", sync);
  clearBtnEl.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    inputEl.value = "";
    sync();
    inputEl.focus();
    if (typeof onCleared === "function") onCleared();
  });
  sync();
}

function initFrontFilterMultiSelectDefault(selectEl) {
  if (!selectEl?.multiple) return;
  Array.from(selectEl.options).forEach((o) => {
    o.selected = false;
  });
}

function frontFilterSelectEls() {
  return [els.filterLeadQuick, els.filterLyricistQuick, els.filterComposerQuick, els.formatSelect, els.tagSelect, els.languageSelect, els.genreSelect].filter(Boolean);
}

function frontFilterGenreIds() {
  const names = filterDropdownSelectedRawValues(els.genreSelect);
  if (!names.length) return [];
  const byName = new Map((state.filters?.genres || []).map((g) => [g.name, g.id]));
  return names.map((n) => byName.get(n)).filter((id) => id != null);
}

function frontHasActiveFilters() {
  const kw = (els.libraryKeywordInput?.value || "").trim();
  if (kw) return true;
  return frontFilterSelectEls().some((el) => filterDropdownSelectedRawValues(el).length > 0);
}

function updateFrontResetVisibility() {
  if (!els.resetFrontFiltersBtn) return;
  els.resetFrontFiltersBtn.classList.toggle("hidden", !frontHasActiveFilters());
}

function resetFrontSongListFilters() {
  if (els.libraryKeywordInput) els.libraryKeywordInput.value = "";
  if (els.libraryKeywordClearBtn) els.libraryKeywordClearBtn.classList.add("hidden");
  frontFilterSelectEls().forEach((el) => {
    if (el.multiple) {
      initFrontFilterMultiSelectDefault(el);
      syncSearchableSelectTrigger(el);
    } else {
      el.value = "";
    }
  });
  setFrontFiltersPanelOpen(false);
  loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
}

function setFrontFiltersPanelOpen(open) {
  if (!els.frontFilterSection || !els.frontToggleFilterBtn) return;
  els.frontFilterSection.classList.toggle("hidden", !open);
  els.frontFilterSection.setAttribute("aria-hidden", open ? "false" : "true");
  els.frontToggleFilterBtn.setAttribute("aria-expanded", open ? "true" : "false");
  els.frontToggleFilterBtn.textContent = open ? "收起筛选" : "更多筛选";
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

function escapeHtml(str) {
  const s = str == null ? "" : String(str);
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

function escSelectAttr(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;");
}

function normalizeDownloadFmt(f) {
  return String(f || "").toLowerCase().replace(/^\./, "").trim();
}

function formatsFromSong(song) {
  if (!song) return [];
  const v = song.file_variants || [];
  const fromVariants = v.map((x) => normalizeDownloadFmt(x.format)).filter(Boolean);
  if (fromVariants.length) return [...new Set(fromVariants)].sort();
  const fm = song.formats || [];
  if (fm.length) return [...new Set(fm.map((x) => normalizeDownloadFmt(x)).filter(Boolean))].sort();
  if (song.file_format) return [normalizeDownloadFmt(song.file_format)].filter(Boolean);
  return [];
}

function unionFormatsFromSongs(songs) {
  const set = new Set();
  songs.forEach((s) => formatsFromSong(s).forEach((f) => set.add(f)));
  return [...set].sort();
}

function songDownloadUrl(songId, formatList) {
  const p = new URLSearchParams();
  formatList.forEach((f) => p.append("formats", f));
  const q = p.toString();
  return getApiUrl(`/songs/${songId}/download${q ? `?${q}` : ""}`);
}

async function ensureSongFormatSource(song) {
  if (!song?.id) return song;
  if (formatsFromSong(song).length) return song;
  const detail = await request(`/songs/${song.id}`);
  return {
    id: song.id,
    title: detail.title,
    file_variants: (detail.files || []).map((f) => ({ file_id: f.id, format: f.format })),
    formats: (detail.files || []).map((f) => f.format).filter(Boolean),
  };
}

function openDownloadFormatsPicker(songs, unionFormats) {
  return new Promise((resolve) => {
    const overlay = els.downloadFormatsOverlay;
    const hint = els.downloadFormatsHint;
    const listEl = els.downloadFormatsList;
    if (!overlay || !listEl || !hint) {
      resolve(null);
      return;
    }
    const one = songs[0] || {};
    hint.textContent = `「${one.title || one.id || "歌曲"}」：勾选要下载的格式（多选将打包为 ZIP，与后台一致）`;

    listEl.innerHTML = unionFormats
      .map((fmt) => {
        const safe = String(fmt).replace(/"/g, "");
        return `<label class="download-format-option"><input type="checkbox" name="dlfmt" value="${safe}" checked /><span>${escapeHtml(fmt.toUpperCase())}</span></label>`;
      })
      .join("");

    const cleanup = () => {
      els.downloadFormatsConfirmBtn?.removeEventListener("click", onConfirm);
      els.downloadFormatsCancelBtn?.removeEventListener("click", onCancel);
      els.downloadFormatsCloseBtn?.removeEventListener("click", onCancel);
      overlay.removeEventListener("click", onBackdrop);
    };

    const finish = (val) => {
      overlay.classList.add("hidden");
      cleanup();
      resolve(val);
    };

    const onConfirm = () => {
      const checked = Array.from(listEl.querySelectorAll('input[name="dlfmt"]:checked')).map((i) => i.value);
      if (!checked.length) {
        showToast("请至少选择一种格式", "error");
        return;
      }
      finish(checked);
    };
    const onCancel = () => finish(null);
    const onBackdrop = (e) => {
      if (e.target === overlay) onCancel();
    };

    els.downloadFormatsConfirmBtn?.addEventListener("click", onConfirm);
    els.downloadFormatsCancelBtn?.addEventListener("click", onCancel);
    els.downloadFormatsCloseBtn?.addEventListener("click", onCancel);
    overlay.addEventListener("click", onBackdrop);
    overlay.classList.remove("hidden");
  });
}

/** 与后台单曲下载一致：多格式弹窗勾选；单格式直链 GET /songs/{id}/download；多文件服务端 ZIP */
async function startSongDownloadFlow(songs) {
  if (!songs?.length) return;
  try {
    const list = await Promise.all(songs.map(ensureSongFormatSource));
    const union = unionFormatsFromSongs(list);
    if (!union.length) {
      showToast("没有可下载的音频格式", "error");
      return;
    }
    const run = (selectedFormats) => {
      window.location.href = songDownloadUrl(list[0].id, selectedFormats);
      showToast("正在下载…", "success");
    };
    if (union.length === 1) {
      run([union[0]]);
      return;
    }
    const selected = await openDownloadFormatsPicker(list, union);
    if (!selected?.length) return;
    run(selected);
  } catch (err) {
    showToast(`下载失败: ${err.message || err}`, "error");
  }
}

function formatRoleNamesCell(names) {
  const list = names || [];
  return list.length ? escapeHtml(list.join("、")) : "—";
}

function renderFilterOptions() {
  if (els.filterLeadQuick) {
    els.filterLeadQuick.innerHTML = (state.filters?.lead_artists || [])
      .map((name) => `<option value="${escSelectAttr(name)}">${escapeHtml(name)}</option>`)
      .join("");
  }
  if (els.filterLyricistQuick) {
    els.filterLyricistQuick.innerHTML = (state.filters?.lyricists || [])
      .map((name) => `<option value="${escSelectAttr(name)}">${escapeHtml(name)}</option>`)
      .join("");
  }
  if (els.filterComposerQuick) {
    els.filterComposerQuick.innerHTML = (state.filters?.composers || [])
      .map((name) => `<option value="${escSelectAttr(name)}">${escapeHtml(name)}</option>`)
      .join("");
  }
  if (els.formatSelect) {
    els.formatSelect.innerHTML = (state.filters?.formats || [])
      .map((v) => `<option value="${escSelectAttr(v)}">${escapeHtml(v.toUpperCase())}</option>`)
      .join("");
  }
  if (els.tagSelect) {
    els.tagSelect.innerHTML = (state.filters?.tags || [])
      .map((tag) => `<option value="${tag.id}">${escapeHtml(tag.name)}</option>`)
      .join("");
  }
  if (els.languageSelect) {
    els.languageSelect.innerHTML = (state.filters?.languages || [])
      .map((lang) => `<option value="${escSelectAttr(lang.name)}">${escapeHtml(lang.name)}</option>`)
      .join("");
  }
  if (els.genreSelect) {
    els.genreSelect.innerHTML = (state.filters?.genres || [])
      .map((genre) => `<option value="${escSelectAttr(genre.name)}">${escapeHtml(genre.name)}</option>`)
      .join("");
  }
  frontFilterSelectEls().forEach((sel) => {
    initFrontFilterMultiSelectDefault(sel);
    ensureSearchableSelect(sel);
    refreshSearchableSelectOptions(sel);
  });
  updateFrontResetVisibility();
}

async function loadFilterOptions() {
  state.filters = await request("/admin/filter-options");
  renderFilterOptions();
}

async function loadLibraryStats() {
  const stats = await request("/library/stats");
  state.librarySongCount = stats.song_count || 0;
  if (els.sidebarSongCount) els.sidebarSongCount.textContent = String(state.librarySongCount);
}

let frontUserMenuInteractAfter = 0;

function setFrontUserMenuOpen(open) {
  if (!els.frontUserMenu || !els.frontUserMenuBtn) return;
  els.frontUserMenu.classList.toggle("hidden", !open);
  els.frontUserMenuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  if (open) {
    frontUserMenuInteractAfter = performance.now() + 350;
    els.frontUserMenu.style.pointerEvents = "none";
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (!els.frontUserMenu?.classList.contains("hidden")) {
          els.frontUserMenu.style.pointerEvents = "";
        }
      });
    });
  } else {
    els.frontUserMenu.style.pointerEvents = "";
  }
}

function closeFrontUserMenu() {
  setFrontUserMenuOpen(false);
}

function handleFrontUserMenuItem(action) {
  if (els.frontUserMenu?.classList.contains("hidden")) return;
  if (performance.now() < frontUserMenuInteractAfter) return;
  setFrontUserMenuOpen(false);
  action();
}

const FRONT_SIDEBAR_COLLAPSED_KEY = "pm.sidebarCollapsed.front";

function readSidebarCollapsedPref(key) {
  try {
    return localStorage.getItem(key) === "1";
  } catch {
    return false;
  }
}

function writeSidebarCollapsedPref(key, collapsed) {
  try {
    localStorage.setItem(key, collapsed ? "1" : "0");
  } catch {
    /* ignore storage failures */
  }
}

function setFrontSidebarCollapsed(collapsed) {
  const shell = document.querySelector(".front-app .app-shell");
  const btn = document.querySelector("#frontSidebarCollapseBtn");
  if (!shell || !btn) return;
  shell.classList.toggle("is-sidebar-collapsed", collapsed);
  btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
  btn.setAttribute("aria-label", collapsed ? "展开侧栏" : "收起侧栏");
}

function initFrontSidebarCollapse() {
  const shell = document.querySelector(".front-app .app-shell");
  const btn = document.querySelector("#frontSidebarCollapseBtn");
  if (!shell || !btn || btn.dataset.skSidebarCollapseBound === "1") return;
  btn.dataset.skSidebarCollapseBound = "1";
  setFrontSidebarCollapsed(readSidebarCollapsedPref(FRONT_SIDEBAR_COLLAPSED_KEY));
  btn.addEventListener("click", () => {
    const collapsed = !shell.classList.contains("is-sidebar-collapsed");
    setFrontSidebarCollapsed(collapsed);
    writeSidebarCollapsedPref(FRONT_SIDEBAR_COLLAPSED_KEY, collapsed);
  });
}

function initFrontUserMenu() {
  if (!els.frontUserMenu || !els.frontUserMenuBtn) return;
  if (els.frontUserMenuBtn.dataset.skUserMenuBound === "1") return;
  els.frontUserMenuBtn.dataset.skUserMenuBound = "1";
  els.frontUserMenuBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    setFrontUserMenuOpen(els.frontUserMenu.classList.contains("hidden"));
  });
}

function buildFrontSongListQueryParams() {
  const params = new URLSearchParams();
  const keyword = (els.libraryKeywordInput?.value || "").trim();
  if (keyword) params.set("keyword", keyword);
  for (const v of filterDropdownSelectedRawValues(els.filterLeadQuick)) params.append("lead_artists", v);
  for (const v of filterDropdownSelectedRawValues(els.filterLyricistQuick)) params.append("lyricists", v);
  for (const v of filterDropdownSelectedRawValues(els.filterComposerQuick)) params.append("composers", v);
  for (const v of filterDropdownSelectedRawValues(els.formatSelect)) params.append("formats", v);
  for (const v of filterDropdownSelectedRawValues(els.tagSelect)) params.append("tag_ids", v);
  for (const v of filterDropdownSelectedRawValues(els.languageSelect)) params.append("languages", v);
  frontFilterGenreIds().forEach((id) => params.append("genre_ids", String(id)));
  const offset = (state.songPage - 1) * state.songPageSize;
  params.set("offset", String(offset));
  params.set("limit", String(state.songPageSize));
  return params;
}

function updateFrontPaginationUi() {
  const totalItems = state.songListTotal;
  const pageSize = state.songPageSize;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  if (state.songPage > totalPages) state.songPage = totalPages;
  const rangeStart = totalItems === 0 ? 0 : (state.songPage - 1) * pageSize + 1;
  const rangeEnd = totalItems === 0 ? 0 : Math.min(state.songPage * pageSize, totalItems);
  if (els.frontSongListTotalLabel) {
    els.frontSongListTotalLabel.textContent =
      totalItems === 0 ? "共 0 首" : `显示 ${rangeStart}–${rangeEnd}，共 ${totalItems} 首`;
  }
  if (els.frontPageInfoLabel) {
    els.frontPageInfoLabel.textContent = `第 ${state.songPage} / ${totalPages} 页`;
  }
  if (els.frontPageFirstBtn) els.frontPageFirstBtn.disabled = state.songPage <= 1;
  if (els.frontPagePrevBtn) els.frontPagePrevBtn.disabled = state.songPage <= 1;
  if (els.frontPageNextBtn) els.frontPageNextBtn.disabled = state.songPage >= totalPages;
  if (els.frontPageLastBtn) els.frontPageLastBtn.disabled = state.songPage >= totalPages;
  if (els.frontPageNumbers) {
    const maxButtons = 5;
    let start = Math.max(1, state.songPage - Math.floor(maxButtons / 2));
    let end = Math.min(totalPages, start + maxButtons - 1);
    start = Math.max(1, end - maxButtons + 1);
    els.frontPageNumbers.innerHTML = "";
    for (let p = start; p <= end; p += 1) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `sk-page-btn${p === state.songPage ? " is-active" : ""}`;
      btn.textContent = String(p);
      btn.addEventListener("click", () => {
        if (state.songPage === p) return;
        state.songPage = p;
        loadSongs({ resetPage: false }).catch((err) => showToast(`加载失败: ${err.message}`, "error"));
      });
      els.frontPageNumbers.appendChild(btn);
    }
  }
}

function primaryFormatLabel(song) {
  const fm = formatsFromSong(song);
  if (!fm.length) return "";
  const pref = ["flac", "mp3", "m4a", "aac", "wav", "ogg"];
  const hit = pref.find((p) => fm.includes(p));
  return (hit || fm[0]).toUpperCase();
}

function syncQueue() {
  state.queue = [...state.songs];
  if (state.currentIndex >= state.queue.length) state.currentIndex = state.queue.length - 1;
}

async function loadSongs({ resetPage = true } = {}) {
  if (state.mainNav === "playlists") return;
  if (resetPage) state.songPage = 1;

  const keyword = (els.libraryKeywordInput?.value || "").trim();

  if (state.selectedPlaylistId) {
    const detail = await request(`/playlists/${state.selectedPlaylistId}`);
    let songs = detail.songs;
    if (keyword) {
      const kw = keyword.toLowerCase();
      songs = songs.filter((song) => [song.title, song.artist, song.album].some((v) => (v || "").toLowerCase().includes(kw)));
    }
    const leadVals = filterDropdownSelectedRawValues(els.filterLeadQuick);
    if (leadVals.length) {
      songs = songs.filter((song) => leadVals.includes(song.lead_artist));
    }
    const lyricistVals = filterDropdownSelectedRawValues(els.filterLyricistQuick);
    if (lyricistVals.length) {
      songs = songs.filter((song) => (song.lyricists || []).some((n) => lyricistVals.includes(n)));
    }
    const composerVals = filterDropdownSelectedRawValues(els.filterComposerQuick);
    if (composerVals.length) {
      songs = songs.filter((song) => (song.composers || []).some((n) => composerVals.includes(n)));
    }
    const formatVals = filterDropdownSelectedRawValues(els.formatSelect);
    if (formatVals.length) {
      songs = songs.filter((song) => formatVals.some((f) => (song.formats || []).some((x) => String(x).toLowerCase() === String(f).toLowerCase())));
    }
    const tagIds = filterDropdownSelectedRawValues(els.tagSelect);
    if (tagIds.length && state.filters?.tags?.length) {
      const names = tagIds
        .map((id) => state.filters.tags.find((item) => String(item.id) === String(id))?.name)
        .filter(Boolean);
      if (names.length) {
        songs = songs.filter((song) => {
          const st = song.tags || [];
          return names.some((n) => st.includes(n));
        });
      }
    }
    const langVals = filterDropdownSelectedRawValues(els.languageSelect);
    if (langVals.length) {
      songs = songs.filter((song) => langVals.includes(song.language));
    }
    const genreVals = filterDropdownSelectedRawValues(els.genreSelect);
    if (genreVals.length) {
      songs = songs.filter((song) => genreVals.includes(song.genre));
    }
    state.songs = songs;
    state.songListTotal = songs.length;
  } else {
    const page = await request(`/songs?${buildFrontSongListQueryParams().toString()}`);
    state.songs = page.items || [];
    state.songListTotal = page.total ?? 0;
  }
  syncQueue();
  syncSelectionAfterLoad();
  renderSongList();
  if (!state.selectedPlaylistId) updateFrontPaginationUi();
  if (els.librarySongCount) els.librarySongCount.textContent = String(state.songListTotal || state.songs.length);
  if (els.sidebarSongCount) els.sidebarSongCount.textContent = String(state.librarySongCount || state.songListTotal || state.songs.length);
  updateLibraryViewTitle();
  updateFrontResetVisibility();
  syncNavForPlaylistState();
}

function updateLibraryViewTitle() {
  const titleEl = document.getElementById("libraryViewTitle");
  if (!titleEl) return;
  if (state.selectedPlaylistId == null) {
    titleEl.textContent = "音乐库";
    return;
  }
  const pl = state.playlists.find((p) => songIdEquals(p.id, state.selectedPlaylistId));
  titleEl.textContent = pl?.name || "歌单";
}

function syncFrontChrome() {
  const leadSpace = document.getElementById("headerLeadPlaylistSpace");
  const searchLib = document.getElementById("headerSearchLibrary");
  const actSpace = document.getElementById("headerActionsPlaylistSpace");
  const actDetail = document.getElementById("headerActionsPlaylistDetail");
  const backBtn = document.getElementById("btnBackPlaylistDetail");
  const studioRoot = document.querySelector(".studio-root");
  const inPl = state.mainNav === "playlists";
  const inDet = inPl && state.playlistDetailId != null;
  const inLib = state.mainNav === "library";
  leadSpace?.classList.toggle("hidden", !inPl || inDet);
  if (leadSpace) leadSpace.setAttribute("aria-hidden", !inPl || inDet ? "true" : "false");
  backBtn?.classList.toggle("hidden", !inDet);
  searchLib?.classList.toggle("hidden", inLib);
  if (searchLib) searchLib.setAttribute("aria-hidden", inLib ? "true" : "false");
  studioRoot?.classList.toggle("is-library-view", inLib);
  actSpace?.classList.toggle("hidden", !inPl || inDet);
  actDetail?.classList.toggle("hidden", !inDet);
  if (els.keywordInput) {
    if (inPl && !inDet) {
      els.keywordInput.placeholder = "搜索歌单 / 标签 / 艺人 / 风格…";
    } else if (inDet) {
      els.keywordInput.placeholder = "搜索歌曲 / 艺人 / 专辑…";
    }
  }
}

function updateMainPanels() {
  const songSec = document.getElementById("songBrowseSection");
  const wrap = document.getElementById("playlistRoutesWrap");
  const spacePage = document.getElementById("playlistSpacePage");
  const detailPage = document.getElementById("playlistDetailPage");
  const insp = document.getElementById("inspectorPanel");
  const showPlaylists = state.mainNav === "playlists";
  songSec?.classList.toggle("hidden", showPlaylists);
  wrap?.classList.toggle("hidden", !showPlaylists);
  insp?.classList.toggle("hidden", showPlaylists);
  if (showPlaylists) {
    const detail = state.playlistDetailId != null;
    spacePage?.classList.toggle("hidden", detail);
    detailPage?.classList.toggle("hidden", !detail);
  }
  syncFrontChrome();
}

function syncSelectionAfterLoad() {
  if (!state.songs.length) {
    state.selectedSongId = null;
    renderInspector(null);
    return;
  }
  const still = state.songs.some((s) => songIdEquals(s.id, state.selectedSongId));
  if (!still) state.selectedSongId = state.songs[0].id;
  const sel = state.songs.find((s) => songIdEquals(s.id, state.selectedSongId));
  renderInspector(sel || null);
}

async function loadPlaylists() {
  state.playlists = await request("/playlists");
  renderPlaylists();
}

function songIdEquals(a, b) {
  return a === b || String(a) === String(b);
}

/** 从 afterIdx 之后找下一首可浏览器试听的曲目（循环）；afterIdx 为 -1 时表示从队列头扫描 */
function findNextPlayableQueueIndex(afterIdx) {
  const len = state.queue.length;
  if (!len) return -1;
  for (let step = 1; step <= len; step++) {
    const i = ((afterIdx >= 0 ? afterIdx : -1) + step) % len;
    if (songHasWebPlayableAudio(state.queue[i])) return i;
  }
  return -1;
}

function hashHue(seed) {
  const n = typeof seed === "number" ? seed : String(seed).split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  return 250 + (n % 70);
}

function coverGradient(seed) {
  const h = hashHue(seed);
  return `linear-gradient(145deg, hsl(${h}, 48%, 32%), hsl(${(h + 45) % 360}, 42%, 20%))`;
}

function buildFourCellHtml(seed) {
  let html = "";
  for (let i = 0; i < 4; i += 1) {
    html += `<div class="ps-rec-cell" style="background:${coverGradient(Number(seed) + i * 17)}"></div>`;
  }
  return html;
}

const PS_MOCK_RECS = [
  { title: "深夜华语", count: 36, ago: "昨天更新" },
  { title: "公路摇滚", count: 24, ago: "3 天前" },
  { title: "咖啡爵士", count: 18, ago: "本周更新" },
];

function sortPlaylistsForHub(list) {
  const mode = state.playlistSort;
  const arr = [...list];
  if (mode === "name") return arr.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
  if (mode === "count") return arr.sort((a, b) => (b.song_count || 0) - (a.song_count || 0));
  return arr;
}

async function playPlaylistById(playlistId) {
  const detail = await request(`/playlists/${playlistId}`);
  const songs = detail.songs || [];
  state.selectedPlaylistId = playlistId;
  state.songs = songs;
  syncQueue();
  const idx = findNextPlayableQueueIndex(-1);
  if (idx >= 0) {
    playSong(state.queue[idx].id).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
  } else {
    showToast("歌单中没有可在线试听的曲目", "warning");
  }
}

function applyPlaylistDetailFiltersAndSort() {
  let songs = [...state.playlistDetailAllSongs];
  const kwLocal = (document.getElementById("pdSongFilterInput")?.value || "").trim().toLowerCase();
  const kwHead = (els.keywordInput?.value || "").trim().toLowerCase();
  const k = kwLocal || kwHead;
  if (k) {
    songs = songs.filter((s) => [s.title, s.lead_artist, s.album].some((v) => (v || "").toLowerCase().includes(k)));
  }
  const sort = document.getElementById("pdSongSortSelect")?.value || "order";
  if (sort === "title") songs.sort((a, b) => (a.title || "").localeCompare(b.title || ""));
  else if (sort === "artist") songs.sort((a, b) => (a.lead_artist || "").localeCompare(b.lead_artist || ""));
  state.songs = songs;
  syncQueue();
  syncSelectionAfterLoad();
}

function setSvgRingPct(circleEl, pct) {
  if (!circleEl) return;
  const p = Math.max(0, Math.min(100, pct));
  circleEl.style.strokeDasharray = `${p} ${100 - p}`;
}

function fmtShortDate(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  } catch {
    return "—";
  }
}

function fmtDurationSum(ms) {
  if (!ms) return "0:00:00";
  const sec = Math.floor(ms / 1000);
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function avgMetadataPct(songs) {
  if (!songs.length) return 0;
  let t = 0;
  songs.forEach((s) => {
    t += metadataCompleteness(s).pct;
  });
  return Math.round(t / songs.length);
}

function fillPlaylistDetailChrome(detail) {
  const name = detail.name || "歌单";
  document.getElementById("pdPlaylistTitle").textContent = name;
  document.getElementById("pdFieldName").value = name;
  const descEl = document.getElementById("pdPlaylistDesc");
  const desc = `${name}：共 ${detail.songs?.length || 0} 首曲目，适合日常聆听与整理收藏。`;
  if (descEl) descEl.textContent = desc;
  document.getElementById("pdFieldDesc").value = desc;
  const tagsEl = document.getElementById("pdFieldTags");
  if (tagsEl) {
    tagsEl.innerHTML = ["华语", "精选", "自建"]
      .map((t) => `<span class="pd-tag-pill">${escapeHtml(t)}</span>`)
      .join("");
  }
  const songs = detail.songs || [];
  const totalMs = songs.reduce((acc, s) => acc + (s.duration_ms || 0), 0);
  document.getElementById("pdSongSummary").textContent = `共 ${songs.length} 首歌曲`;
  document.getElementById("pdSongDurationSum").textContent = fmtDurationSum(totalMs);
  const metaAvg = avgMetadataPct(songs);
  document.getElementById("pdRingSongsLbl").textContent = String(songs.length);
  document.getElementById("pdRingDurLbl").textContent = fmtDurationSum(totalMs);
  document.getElementById("pdRingMetaLbl").textContent = `${metaAvg}%`;
  setSvgRingPct(document.getElementById("pdRingSongs"), songs.length ? 92 : 0);
  setSvgRingPct(
    document.getElementById("pdRingDur"),
    totalMs ? Math.min(100, Math.round((totalMs / (24 * 60 * 60 * 1000)) * 100)) : 0
  );
  setSvgRingPct(document.getElementById("pdRingMeta"), metaAvg);

  const collage = document.getElementById("pdHeroCollage");
  if (collage) {
    const slice = songs.slice(0, 4);
    while (slice.length < 4) slice.push({});
    collage.innerHTML = slice
      .map((s, i) => `<div class="pd-hero-cell" style="background:${coverGradient((detail.id || 1) + i * 13)}"></div>`)
      .join("");
    const last = collage.querySelector(".pd-hero-cell:last-child");
    if (last && songs.length > 0) {
      last.classList.add("overlay-more");
      last.textContent = `+${songs.length}`;
    }
  }

  const metaRow = document.getElementById("pdMetaRow");
  if (metaRow) {
    metaRow.innerHTML = `
      <span>SoulKing</span><span class="dot">·</span>
      <span>创建于 2024-05-01</span><span class="dot">·</span>
      <span>公开</span><span class="dot">·</span>
      <span>${songs.length} 首</span><span class="dot">·</span>
      <span>${fmtDurationSum(totalMs)}</span>`;
  }

  const asideT = document.getElementById("pdAsideTimes");
  if (asideT) asideT.textContent = "创建于 2024-05-01 · 更新于最近";

  const sim = document.getElementById("pdSimilarList");
  if (sim) {
    sim.innerHTML = state.playlists
      .filter((p) => !songIdEquals(p.id, detail.id))
      .slice(0, 4)
      .map(
        (p) => `
      <li class="pd-sim-item">
        <div class="pd-sim-thumb" style="background:${coverGradient(p.id)}"></div>
        <div class="pd-sim-meta">
          <div class="t">${escapeHtml(p.name)}</div>
          <div class="sub">${p.song_count || 0} 首 · 88%</div>
        </div>
        <button type="button" class="pd-follow-btn" data-goto-pl="${p.id}">+ 关注</button>
      </li>`
      )
      .join("");
    sim.querySelectorAll("[data-goto-pl]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = Number(btn.getAttribute("data-goto-pl"));
        if (id) openPlaylistDetail(id).catch((err) => showToast(err.message, "error"));
      });
    });
  }
}

async function refreshPlaylistDetailData() {
  const id = state.playlistDetailId;
  if (id == null) return;
  const detail = await request(`/playlists/${id}`);
  state.playlistDetailAllSongs = detail.songs || [];
  state.selectedPlaylistId = id;
  applyPlaylistDetailFiltersAndSort();
  fillPlaylistDetailChrome(detail);
  renderSongList();
}

async function openPlaylistDetail(playlistId) {
  state.playlistDetailId = playlistId;
  state.selectedPlaylistId = playlistId;
  updateMainPanels();
  try {
    await refreshPlaylistDetailData();
  } catch (err) {
    showToast(`加载歌单失败: ${err.message}`, "error");
    state.playlistDetailId = null;
    state.selectedPlaylistId = null;
    updateMainPanels();
  }
  syncNavForPlaylistState();
}

function closePlaylistDetail() {
  state.playlistDetailId = null;
  state.selectedPlaylistId = null;
  state.playlistDetailAllSongs = [];
  document.getElementById("pdSongFilterInput").value = "";
  updateMainPanels();
  renderPlaylistHub();
  syncNavForPlaylistState();
}

function renderPlaylistHub() {
  if (state.mainNav !== "playlists" || state.playlistDetailId) return;
  const recRow = document.getElementById("playlistRecommendRow");
  const grid = document.getElementById("playlistCardGrid");
  if (!recRow || !grid) return;
  const filter = (state.playlistHubFilter || "").toLowerCase();
  const pls = sortPlaylistsForHub(state.playlists).filter((p) => {
    if (!filter) return true;
    return (p.name || "").toLowerCase().includes(filter);
  });

  recRow.innerHTML = "";
  const recItems = [];
  for (let i = 0; i < 3; i += 1) {
    const p = pls[i];
    if (p) {
      recItems.push({ type: "pl", pl: p });
    } else {
      const m = PS_MOCK_RECS[i] || PS_MOCK_RECS[0];
      recItems.push({ type: "mock", label: m.title, count: m.count, ago: m.ago, seed: 200 + i });
    }
  }

  recItems.forEach((item) => {
    const card = document.createElement("article");
    card.className = "ps-rec-card";
    if (item.type === "pl") {
      card.dataset.playlistId = String(item.pl.id);
      card.innerHTML = `
        <div class="ps-rec-grid">${buildFourCellHtml(item.pl.id)}</div>
        <div class="ps-rec-foot">
          <strong>${escapeHtml(item.pl.name)}</strong>
          <div class="ps-rec-meta">${item.pl.song_count || 0} 首歌曲 · 最近更新</div>
        </div>
        <button type="button" class="ps-rec-play" aria-label="播放">▶</button>`;
      card.addEventListener("click", (e) => {
        if (e.target.closest(".ps-rec-play")) return;
        openPlaylistDetail(item.pl.id).catch(() => {});
      });
      card.querySelector(".ps-rec-play").addEventListener("click", (e) => {
        e.stopPropagation();
        playPlaylistById(item.pl.id).catch((err) => showToast(err.message, "error"));
      });
    } else {
      card.innerHTML = `
        <div class="ps-rec-grid">${buildFourCellHtml(item.seed)}</div>
        <div class="ps-rec-foot">
          <strong>${escapeHtml(item.label)}</strong>
          <div class="ps-rec-meta">${item.count} 首歌曲 · ${escapeHtml(item.ago)}</div>
        </div>
        <button type="button" class="ps-rec-play" aria-label="播放">▶</button>`;
      card.addEventListener("click", (e) => {
        if (e.target.closest(".ps-rec-play")) return;
        showToast("打开推荐歌单", "info");
      });
      card.querySelector(".ps-rec-play").addEventListener("click", (e) => {
        e.stopPropagation();
        showToast("推荐试听即将接入", "info");
      });
    }
    recRow.appendChild(card);
  });

  const more = document.createElement("article");
  more.className = "ps-rec-card";
  more.style.flex = "0 0 168px";
  more.innerHTML = `<div style="min-height:146px;display:grid;place-items:center;background:var(--sk-panel-2)"><span style="font-size:40px;opacity:0.35">♪</span></div>
    <div class="ps-rec-foot"><strong>更多推荐</strong><div class="ps-rec-meta">发现更多</div></div>`;
  more.addEventListener("click", () => showToast("推荐流即将接入", "info"));
  recRow.appendChild(more);

  grid.innerHTML = "";
  const libCard = document.createElement("button");
  libCard.type = "button";
  libCard.className = "ps-pl-card is-lib";
  libCard.innerHTML = `
    <div class="ps-pl-grid">${buildFourCellHtml("lib")}</div>
    <div class="ps-pl-foot"><strong>音乐库</strong><div class="ps-pl-meta">${state.librarySongCount} 首歌曲 · 全库浏览</div></div>`;
  libCard.addEventListener("click", () => {
    state.mainNav = "library";
    state.selectedPlaylistId = null;
    updateMainPanels();
    loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
    syncNavForPlaylistState();
  });
  grid.appendChild(libCard);

  pls.forEach((pl) => {
    const card = document.createElement("article");
    card.className = "ps-pl-card";
    card.dataset.playlistId = String(pl.id);
    card.innerHTML = `
      <div class="ps-pl-grid">${buildFourCellHtml(pl.id)}</div>
      <div class="ps-pl-foot"><strong>${escapeHtml(pl.name)}</strong><div class="ps-pl-meta">${pl.song_count || 0} 首歌曲 · 最近更新</div></div>
      <button type="button" class="ps-pl-play" aria-label="播放">▶</button>`;
    card.addEventListener("click", (e) => {
      if (e.target.closest(".ps-pl-play")) return;
      openPlaylistDetail(pl.id).catch(() => {});
    });
    card.querySelector(".ps-pl-play").addEventListener("click", (e) => {
      e.stopPropagation();
      playPlaylistById(pl.id).catch((err) => showToast(err.message, "error"));
    });
    grid.appendChild(card);
  });

  const newCard = document.createElement("button");
  newCard.type = "button";
  newCard.className = "ps-pl-card is-new";
  newCard.innerHTML = `<span style="font-size:38px;line-height:1;color:var(--sk-accent)">+</span><span style="font-size:13px">新建歌单</span>`;
  newCard.addEventListener("click", () => els.createPlaylistBtn?.click());
  grid.appendChild(newCard);

  const totalEl = document.getElementById("playlistTotalCount");
  if (totalEl) totalEl.textContent = String(pls.length);
  const sp = document.getElementById("psStatPlaylists");
  const ss = document.getElementById("psStatSongs");
  const sh = document.getElementById("psStatHours");
  if (sp) sp.textContent = String(state.playlists.length);
  if (ss) ss.textContent = String(state.librarySongCount);
  const estH = Math.max(0, Math.round(((state.librarySongCount || 0) * 215) / 3600));
  if (sh) sh.textContent = `${estH}h`;

  const asideRecent = document.getElementById("psAsideRecentList");
  if (asideRecent) {
    asideRecent.innerHTML = pls
      .slice(0, 5)
      .map(
        (p) => `
      <li>
        <div class="thumb" style="background:${coverGradient(p.id)}"></div>
        <div class="meta"><div class="t">${escapeHtml(p.name)}</div><div class="sub">最近更新</div></div>
      </li>`
      )
      .join("");
  }
}

function renderPlaylists() {
  if (state.mainNav === "playlists" && !state.playlistDetailId) renderPlaylistHub();
  syncNavForPlaylistState();
}

/** 侧栏：音乐库与当前主内容区一致 */
function syncNavForPlaylistState() {
  document.querySelectorAll(".sk-nav-item[data-sk-nav]").forEach((b) => {
    const k = b.getAttribute("data-sk-nav");
    if (k === "library") {
      b.classList.toggle("is-active", state.mainNav === "library");
    } else {
      b.classList.remove("is-active");
    }
  });
}

async function playSong(songId, preferredFormat = "", failureAttempt = 0) {
  if (state.queue.length && failureAttempt >= state.queue.length) {
    showToast("列表中的歌曲均无法播放", "error");
    return;
  }
  const targetSong =
    state.songs.find((s) => s.id === songId) ||
    state.queue.find((s) => s.id === songId);
  if (targetSong && !songHasWebPlayableAudio(targetSong)) {
    let badIdx = state.queue.findIndex((s) => songIdEquals(s.id, songId));
    if (badIdx < 0) badIdx = state.songs.findIndex((s) => songIdEquals(s.id, songId));
    if (badIdx < 0) {
      const idx = findNextPlayableQueueIndex(state.currentIndex);
      if (idx >= 0) {
        showToast("当前曲目无可播格式，已跳过", "warning");
        playSong(state.queue[idx].id, "", failureAttempt + 1).catch(() => {});
      } else {
        showToast("列表中的歌曲均无法播放", "error");
      }
      return;
    }
    state.currentIndex = badIdx;
    renderSongList();
    const idx = nextIndexAfterPlaybackFailure();
    if (idx >= 0 && state.queue[idx] && songHasWebPlayableAudio(state.queue[idx])) {
      showToast("当前曲目无可播格式，已跳过", "warning");
      playSong(state.queue[idx].id, "", failureAttempt + 1).catch(() => {});
    } else {
      const fallback = findNextPlayableQueueIndex(badIdx);
      if (fallback >= 0) {
        showToast("当前曲目无可播格式，已跳过", "warning");
        playSong(state.queue[fallback].id, "", failureAttempt + 1).catch(() => {});
      } else {
        showToast("列表中的歌曲均无法播放", "error");
      }
    }
    return;
  }
  const url = preferredFormat ? `/songs/${songId}/play?preferred_format=${preferredFormat}` : `/songs/${songId}/play`;
  const playInfo = await request(url);
  state.currentIndex = state.queue.findIndex((item) => songIdEquals(item.id, songId));
  renderSongList();
  const audio = els.audioPlayer;
  const streamSrc = resolveMediaSrc(playInfo.stream_url);
  frontAudioPlayGeneration += 1;
  const gen = frontAudioPlayGeneration;

  const skipToNext = (message) => {
    if (gen !== frontAudioPlayGeneration) return;
    if (state.playMode === "single-loop") {
      showToast("当前曲目无法播放", "error");
      return;
    }
    const idx = nextIndexAfterPlaybackFailure();
    if (idx >= 0 && state.queue[idx]) {
      showToast(message || "当前曲目无法播放，已跳过", "warning");
      playSong(state.queue[idx].id, "", failureAttempt + 1).catch(() => {});
    } else {
      showToast("播放失败", "error");
    }
  };

  const onErr = () => {
    audio.removeEventListener("error", onErr);
    if (gen !== frontAudioPlayGeneration) return;
    skipToNext("当前曲目无法播放，已跳过");
  };
  audio.addEventListener("error", onErr, { once: true });

  audio.src = streamSrc;
  updatePlayerShell(targetSong);
  updateNextTrackHint();
  syncTransportDecorations();
  updatePlayPauseIcon();
  loadSongLyrics(songId).catch(() => {});
  try {
    await audio.play();
  } catch (_err) {
    audio.removeEventListener("error", onErr);
    if (gen !== frontAudioPlayGeneration) return;
    skipToNext("当前曲目无法播放，已跳过");
  }
}

function nextIndex() {
  if (!state.queue.length) return -1;
  if (state.playMode === "single-loop") return state.currentIndex;
  if (state.playMode === "shuffle") return Math.floor(Math.random() * state.queue.length);
  if (state.currentIndex < state.queue.length - 1) return state.currentIndex + 1;
  if (state.playMode === "list-loop") return 0;
  // sequence：顺序播放到最后一首后停止（与列表循环不同）
  return -1;
}

/** 非单曲模式下跳过失败曲目：若 nextIndex 仍指向当前索引（如随机抽到同一首），则顺序进一位以免死循环 */
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

function playCurrentPlaylist() {
  if (!state.queue.length) return showToast("当前歌单暂无歌曲", "error");
  const first = state.queue.find((s) => songHasWebPlayableAudio(s));
  if (!first) return showToast("当前列表中歌曲均无可试听格式（如仅 APE）", "error");
  playSong(first.id).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
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
  await loadPlaylists();
  if (state.playlistDetailId != null) {
    await refreshPlaylistDetailData();
  } else {
    await loadSongs();
  }
}

const MSG_NO_WEB_PLAY_PREVIEW =
  "该歌曲仅有 APE 等格式，浏览器无法在线试听，请下载后使用本地播放器或补充 MP3/FLAC 等可播格式";
const MSG_NO_WEB_PLAY_ADD_PLAYLIST =
  "该歌曲仅有 APE 等格式，无可在线试听的音频，暂不支持加入歌单（歌单需能正常播放）";

const SCROLL_TABLE_HEAD_GAP = 4;

function frontIsLibraryPaginated() {
  return state.mainNav === "library" && !state.selectedPlaylistId;
}

function frontGlobalIndexFromLocal(localIdx) {
  if (!frontIsLibraryPaginated()) return localIdx;
  return (state.songPage - 1) * state.songPageSize + localIdx;
}

function frontLocalIndexFromGlobal(globalIdx) {
  return frontIsLibraryPaginated() ? globalIdx % state.songPageSize : globalIdx;
}

function frontPageFromGlobal(globalIdx) {
  return Math.floor(globalIdx / state.songPageSize) + 1;
}

function scrollTableRowIntoView(tbody, rowSelector = "tr.is-active") {
  if (!tbody) return;
  const active = tbody.querySelector(rowSelector);
  if (!active) return;
  requestAnimationFrame(() => {
    const wrap = tbody.closest(".song-table-wrap") || tbody.closest(".pd-table-wrap");
    if (!wrap) return;
    const thead = wrap.querySelector("thead");
    const theadH = (thead?.offsetHeight ?? 0) + SCROLL_TABLE_HEAD_GAP;
    const wrapRect = wrap.getBoundingClientRect();
    const rowRect = active.getBoundingClientRect();
    const rowTopInWrap = wrap.scrollTop + (rowRect.top - wrapRect.top);
    const rowBottomInWrap = rowTopInWrap + active.offsetHeight;
    const visibleTop = wrap.scrollTop + theadH;
    const visibleBottom = wrap.scrollTop + wrap.clientHeight;
    let nextTop = wrap.scrollTop;
    if (rowTopInWrap < visibleTop) {
      nextTop = rowTopInWrap - theadH;
    } else if (rowBottomInWrap > visibleBottom) {
      nextTop = rowBottomInWrap - wrap.clientHeight;
    } else {
      return;
    }
    wrap.scrollTo({ top: Math.max(0, nextTop), behavior: "smooth" });
  });
}

function scrollActiveSongItemIntoView() {
  const inDetail = state.mainNav === "playlists" && state.playlistDetailId != null;
  const list = inDetail ? els.playlistDetailSongList : els.songList;
  scrollTableRowIntoView(list);
}

async function playSongAtGlobalIndex(globalIdx) {
  if (frontIsLibraryPaginated()) {
    const requiredPage = frontPageFromGlobal(globalIdx);
    if (requiredPage !== state.songPage) {
      state.songPage = requiredPage;
      await loadSongs({ resetPage: false });
    }
  }
  const localIdx = frontLocalIndexFromGlobal(globalIdx);
  const song = state.queue[localIdx];
  if (!song) {
    showToast("无法定位歌曲", "error");
    return;
  }
  await playSong(song.id);
}

async function playAdjacentSong(direction) {
  const paginated = frontIsLibraryPaginated();
  const total = paginated ? state.songListTotal : state.queue.length;
  if (total <= 0 || !state.queue.length) return;

  if (state.playMode === "shuffle") {
    const idx = Math.floor(Math.random() * state.queue.length);
    await playSong(state.queue[idx].id);
    return;
  }
  if (state.playMode === "single-loop" && state.currentIndex >= 0) {
    await playSong(state.queue[state.currentIndex].id);
    return;
  }

  if (state.currentIndex < 0) {
    const first = state.queue.find((s) => songHasWebPlayableAudio(s));
    if (first) await playSong(first.id);
    return;
  }

  let globalIdx = paginated ? frontGlobalIndexFromLocal(state.currentIndex) : state.currentIndex;
  let nextGlobal = globalIdx + direction;
  if (state.playMode === "list-loop") {
    if (nextGlobal < 0) nextGlobal = total - 1;
    if (nextGlobal >= total) nextGlobal = 0;
  } else if (nextGlobal < 0 || nextGlobal >= total) {
    return;
  }

  if (paginated) {
    await playSongAtGlobalIndex(nextGlobal);
  } else {
    await playSong(state.queue[nextGlobal].id);
  }
}

function songReleaseYear(song) {
  const d = song?.release_date;
  if (!d) return "—";
  const y = String(d).slice(0, 4);
  return /^\d{4}$/.test(y) ? y : "—";
}

function metadataCompleteness(song) {
  const checks = [
    song.title,
    song.album,
    song.lead_artist,
    (song.lyricists || []).length > 0,
    (song.composers || []).length > 0,
    song.genre,
    song.language,
    (song.tags || []).length > 0,
    song.duration_ms,
  ];
  const filled = checks.filter((v) => v != null && v !== "" && v !== false && v !== 0).length;
  const total = checks.length;
  const pct = total ? Math.round((filled / total) * 100) : 0;
  return { pct, filled, total };
}

function updatePlayerShell(song) {
  if (els.playerBarTitle) els.playerBarTitle.textContent = song?.title || "暂无播放";
  if (els.playerBarArtist) els.playerBarArtist.textContent = song?.lead_artist || "—";
  if (els.playerThumb) {
    els.playerThumb.innerHTML = "";
    els.playerThumb.textContent = "♪";
  }
}

async function loadSongLyrics(songId) {
  if (!songId) {
    state.lyricLines = [];
    state.lyricSongId = null;
    state.lyricContent = "";
    syncPlayerLyricLine(0);
    return;
  }
  const data = await loadSongLyricsViaRequest(request, songId);
  state.lyricSongId = songId;
  if (!data) {
    state.lyricLines = [];
    state.lyricContent = "";
    syncPlayerLyricLine(0);
    if (state.inspectorTab === "lyrics" && state.selectedSongId === songId) {
      const song = state.songs.find((s) => s.id === songId) || state.queue.find((s) => s.id === songId);
      if (song) renderInspectorPanel(song);
    }
    return;
  }
  state.lyricLines = data.lines;
  state.lyricContent = data.content;
  syncPlayerLyricLine((els.audioPlayer?.currentTime || 0) * 1000);
  if (state.inspectorTab === "lyrics" && state.selectedSongId === songId) {
    const song = state.songs.find((s) => s.id === songId) || state.queue.find((s) => s.id === songId);
    if (song) renderInspectorPanel(song);
  }
}

function syncPlayerLyricLine(timeMs) {
  if (!els.playerLyricLine) return;
  if (!state.lyricLines?.length || state.lyricSongId == null) {
    if (lastPlayerLyricText !== LYRIC_PLACEHOLDER) {
      els.playerLyricLine.textContent = LYRIC_PLACEHOLDER;
      lastPlayerLyricText = LYRIC_PLACEHOLDER;
    }
    return;
  }
  const text = findLyricLineAtTime(state.lyricLines, timeMs);
  const display = text || "···";
  if (display !== lastPlayerLyricText) {
    els.playerLyricLine.textContent = display;
    lastPlayerLyricText = display;
  }
}

function readStoredPlayerLyricsVisible() {
  try {
    const raw = localStorage.getItem(LYRICS_VISIBLE_STORAGE_KEY);
    if (raw === "0") return false;
    if (raw === "1") return true;
  } catch {
    /* ignore */
  }
  return true;
}

function persistPlayerLyricsVisible(visible) {
  try {
    localStorage.setItem(LYRICS_VISIBLE_STORAGE_KEY, visible ? "1" : "0");
  } catch {
    /* ignore */
  }
}

function applyPlayerLyricsVisible(visible) {
  const show = Boolean(visible);
  document.querySelector(".front-app")?.setAttribute("data-lyrics-visible", show ? "true" : "false");
  els.studioPlayer?.classList.toggle("is-lyrics-hidden", !show);
  const btn = els.playerLyricsToggleBtn;
  if (btn) {
    btn.setAttribute("aria-pressed", show ? "true" : "false");
    btn.title = show ? "隐藏歌词" : "显示歌词";
    btn.classList.toggle("is-active", show);
  }
}

function togglePlayerLyricsVisible() {
  const currentlyHidden = els.studioPlayer?.classList.contains("is-lyrics-hidden") ?? false;
  const show = currentlyHidden;
  applyPlayerLyricsVisible(show);
  persistPlayerLyricsVisible(show);
}

function initPlayerLyricsToggle() {
  applyPlayerLyricsVisible(readStoredPlayerLyricsVisible());
  els.playerLyricsToggleBtn?.addEventListener("click", togglePlayerLyricsVisible);
}

function updatePlayPauseIcon() {
  const a = els.audioPlayer;
  const btn = els.playerPlayPauseBtn;
  if (!btn || !a) return;
  btn.textContent = a.paused ? "▶" : "⏸";
}

function updateNextTrackHint() {
  if (!els.playerNextHint) return;
  const idx = nextIndex();
  if (idx < 0 || !state.queue[idx]) {
    els.playerNextHint.textContent = "";
    return;
  }
  const n = state.queue[idx];
  els.playerNextHint.textContent = `下一首：${n.title || "—"} · ${n.lead_artist || ""}`;
}

function formatTimeCompact(sec) {
  if (!sec || !Number.isFinite(sec)) return "0:00";
  const s = Math.floor(sec % 60);
  const m = Math.floor(sec / 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

function syncTransportDecorations() {
  if (els.playModeSelect) els.playModeSelect.value = state.playMode;
}

function renderInspectorDetail(song) {
  const { pct, filled, total } = metadataCompleteness(song);
  const rows = [
    ["作词", (song.lyricists || []).join(" / ") || "—"],
    ["作曲", (song.composers || []).join(" / ") || "—"],
    ["专辑", song.album || "—"],
    ["发行日期", song.release_date || "—"],
    ["风格", song.genre || "—"],
    ["时长", fmtDuration(song.duration_ms)],
    ["格式", (song.formats || []).map((x) => String(x).toUpperCase()).join(", ") || "—"],
  ];
  els.inspectorDetail.innerHTML = `
    <div class="studio-meta-ring-wrap" style="margin-bottom:16px">
      <div class="studio-meta-ring" style="--pct:${pct}">
        <div class="studio-meta-ring-inner"><span>${pct}%</span></div>
      </div>
      <p style="margin:8px 0 0;font-size:12px;color:var(--sk-muted)">已完成字段 ${filled} / ${total}</p>
    </div>
    <dl style="margin:0">
      ${rows.map(([k, v]) => `<div class="studio-detail-row"><dt>${escapeHtml(k)}</dt><dd>${escapeHtml(v)}</dd></div>`).join("")}
    </dl>
    <p style="margin-top:14px;font-size:11px;color:var(--sk-muted-2)">外部置信度来源为示意 UI，未接入实时抓取。</p>
  `;
}

function renderInspectorLyrics(song) {
  if (song.id !== state.lyricSongId) {
    els.inspectorDetail.innerHTML = `<p style="margin:0;font-size:13px;color:var(--sk-muted)">正在加载歌词…</p>`;
    loadSongLyrics(song.id).catch(() => {
      if (state.selectedSongId === song.id && state.inspectorTab === "lyrics") {
        renderInspectorPanel(song);
      }
    });
    return;
  }
  if (!state.lyricContent && !state.lyricLines?.length) {
    els.inspectorDetail.innerHTML = `
      <p style="margin:0 0 8px;font-size:13px;color:var(--sk-text)">暂无 LRC 歌词</p>
      <p style="margin:0;font-size:12px;color:var(--sk-muted)">可将 <code>.lrc</code> 与音频放在同一目录后重新扫描，或在后台编辑页上传替换。</p>
    `;
    return;
  }
  const body = state.lyricContent || state.lyricLines.map((l) => l.text).filter(Boolean).join("\n");
  els.inspectorDetail.innerHTML = `
    <pre class="studio-lyrics-panel" style="margin:0;white-space:pre-wrap;word-break:break-word;font-size:12px;line-height:1.6;color:var(--sk-text)">${escapeHtml(body)}</pre>
  `;
}

function renderInspectorPanel(song) {
  if (!song || !els.inspectorDetail) return;
  if (state.inspectorTab === "lyrics") {
    renderInspectorLyrics(song);
  } else if (state.inspectorTab === "related" || state.inspectorTab === "files") {
    els.inspectorDetail.innerHTML = `<p style="margin:0;font-size:13px;color:var(--sk-muted)">该面板即将接入。</p>`;
  } else {
    renderInspectorDetail(song);
  }
}

function renderInspector(song) {
  if (!els.inspectorTitle || !els.inspectorArtist || !els.inspectorDetail || !els.inspectorEmpty) return;
  if (!song) {
    els.inspectorEmpty.classList.remove("hidden");
    els.inspectorDetail.classList.add("hidden");
    els.inspectorTitle.textContent = "未选择曲目";
    els.inspectorArtist.textContent = "在列表中选择一首歌曲";
    if (els.inspectorPlayBtn) els.inspectorPlayBtn.disabled = true;
    return;
  }
  els.inspectorEmpty.classList.add("hidden");
  els.inspectorDetail.classList.remove("hidden");
  els.inspectorTitle.textContent = song.title || "—";
  els.inspectorArtist.textContent = song.lead_artist || "—";
  if (els.inspectorPlayBtn) els.inspectorPlayBtn.disabled = !songHasWebPlayableAudio(song);
  renderInspectorPanel(song);
}

function songRowInnerHtml(song, index) {
  const canWeb = songHasWebPlayableAudio(song);
  const tags = (song.tags || []).slice(0, 3);
  const extra = (song.tags || []).length > 3 ? ` +${(song.tags || []).length - 3}` : "";
  const isPlaying = state.currentIndex >= 0 && state.queue[state.currentIndex]?.id === song.id;
  const wave = isPlaying ? '<span class="sk-wave-mini" aria-hidden="true"></span>' : "";
  const fmt = primaryFormatLabel(song);
  return `
    <td class="sk-col-idx">${index + 1}</td>
    <td class="sk-col-title">
      <div class="sk-title-cell">
        <div class="sk-title-stack">
          <div class="sk-t">${escapeHtml(song.title || "—")} ${wave}</div>
        </div>
      </div>
    </td>
    <td class="sk-col-meta">${escapeHtml(song.lead_artist || "—")}</td>
    <td class="sk-col-meta">${formatRoleNamesCell(song.lyricists)}</td>
    <td class="sk-col-meta">${formatRoleNamesCell(song.composers)}</td>
    <td class="sk-col-meta">${escapeHtml(song.album || "—")}</td>
    <td class="sk-col-meta">${escapeHtml(song.language || "—")}</td>
    <td class="sk-col-meta">${escapeHtml(song.genre || "—")}</td>
    <td class="sk-col-meta">${escapeHtml(song.film_tv || "—")}</td>
    <td class="sk-col-meta">${tags.map((t) => `<span class="sk-pill tag">${escapeHtml(t)}</span>`).join("")}${extra}</td>
    <td class="sk-col-meta">${fmt ? escapeHtml(fmt) : "—"}</td>
    <td class="sk-col-meta">${fmtDuration(song.duration_ms)}</td>
    <td class="sk-col-meta">${escapeHtml(song.release_date || "—")}</td>
    <td class="sk-col-actions" data-stop-row="1">
      <div class="sk-row-more">
        <button type="button" data-role="more" aria-label="更多" title="更多">⋯</button>
        <div class="sk-row-more-menu hidden" data-role="menu">
          ${
            canWeb
              ? `<button type="button" class="sk-row-more-item" data-role="play">▶ 试听</button>`
              : `<button type="button" class="sk-row-more-item" data-role="play" disabled title="${escapeHtml(MSG_NO_WEB_PLAY_PREVIEW)}">▶ 试听</button>`
          }
          ${
            canWeb
              ? `<button type="button" class="sk-row-more-item" data-role="add">＋ 加入歌单</button>`
              : `<button type="button" class="sk-row-more-item" data-role="add" disabled title="${escapeHtml(MSG_NO_WEB_PLAY_ADD_PLAYLIST)}">＋ 加入歌单</button>`
          }
          <button type="button" class="sk-row-more-item" data-role="download">↓ 下载</button>
        </div>
      </div>
    </td>
  `;
}
function songRowPlaylistDetailInnerHtml(song, index) {
  const removable = state.selectedPlaylistId !== null;
  const canWeb = songHasWebPlayableAudio(song);
  const { pct } = metadataCompleteness(song);
  const isPlaying = state.currentIndex >= 0 && state.queue[state.currentIndex]?.id === song.id;
  const wave = isPlaying ? '<span class="sk-wave-mini" aria-hidden="true"></span>' : "";
  return `
    <td class="sk-col-check"><input type="checkbox" class="song-row-check" data-id="${song.id}" aria-label="选择" /></td>
    <td class="pd-col-idx">${index + 1}</td>
    <td class="sk-col-title">
      <div class="sk-title-cell">
        <div class="sk-thumb" aria-hidden="true">♪</div>
        <div class="sk-title-stack">
          <div class="sk-t">${escapeHtml(song.title || "—")} ${wave}</div>
          <div class="sk-sub">${escapeHtml(song.album || "")}</div>
        </div>
      </div>
    </td>
    <td>${escapeHtml(song.lead_artist || "—")}</td>
    <td>${escapeHtml(song.album || "—")}</td>
    <td>${fmtDuration(song.duration_ms)}</td>
    <td>${fmtShortDate(song.created_at)}</td>
    <td style="text-align:center"><div class="sk-meta-gauge" style="--p:${pct}"><span>${pct}%</span></div></td>
    <td>
      <div class="sk-row-actions">
        ${
          canWeb
            ? `<button type="button" data-role="play" title="试听">▶</button>`
            : `<button type="button" data-role="play" disabled title="${escapeHtml(MSG_NO_WEB_PLAY_PREVIEW)}">▶</button>`
        }
        <button type="button" data-role="download" title="下载">↓</button>
        ${removable ? '<button type="button" data-role="delete" title="移除">🗑</button>' : ""}
      </div>
    </td>
  `;
}

function closeAllFrontRowMoreMenus(exceptMenu = null) {
  document.querySelectorAll(".sk-row-more-menu").forEach((node) => {
    if (node === exceptMenu) return;
    node.classList.add("hidden");
    node.classList.remove("sk-row-more-menu-fixed");
    node.style.top = "";
    node.style.left = "";
    node.style.right = "";
    const home = node._skRowMoreHome;
    if (home && node.parentNode === document.body) home.appendChild(node);
  });
}

function returnFrontRowMoreMenuHome(menu) {
  menu.classList.add("hidden");
  menu.classList.remove("sk-row-more-menu-fixed");
  menu.style.top = "";
  menu.style.left = "";
  menu.style.right = "";
  const home = menu._skRowMoreHome;
  if (home && menu.parentNode !== home) home.appendChild(menu);
}

function bindFrontRowMoreMenu(tr, song) {
  const moreBtn = tr.querySelector('[data-role="more"]');
  const menu = tr.querySelector('[data-role="menu"]');
  if (!moreBtn || !menu) return;
  const rowMore = moreBtn.closest(".sk-row-more");

  moreBtn.addEventListener("click", (ev) => {
    ev.stopPropagation();
    closeAllFrontRowMoreMenus(menu);
    const wasHidden = menu.classList.contains("hidden");
    menu.classList.toggle("hidden");
    if (wasHidden) {
      menu._skRowMoreHome = rowMore;
      document.body.appendChild(menu);
      menu.classList.add("sk-row-more-menu-fixed");
      const rect = moreBtn.getBoundingClientRect();
      menu.style.top = `${rect.bottom + 2}px`;
      menu.style.left = `${Math.max(8, rect.right - 120)}px`;
      menu.style.right = "auto";
    } else {
      returnFrontRowMoreMenuHome(menu);
    }
  });

  menu.querySelector('[data-role="play"]')?.addEventListener("click", (e) => {
    e.stopPropagation();
    if (e.currentTarget.disabled) return;
    returnFrontRowMoreMenuHome(menu);
    playSong(song.id).catch((err) => showToast(`试听失败: ${err.message}`, "error"));
  });
  menu.querySelector('[data-role="add"]')?.addEventListener("click", (e) => {
    e.stopPropagation();
    if (e.currentTarget.disabled) return;
    returnFrontRowMoreMenuHome(menu);
    addSongToPlaylist(song.id).catch((err) => showToast(`加入歌单失败: ${err.message}`, "error"));
  });
  menu.querySelector('[data-role="download"]')?.addEventListener("click", async (e) => {
    e.stopPropagation();
    returnFrontRowMoreMenuHome(menu);
    await startSongDownloadFlow([song]);
  });
}

function renderSongList() {
  if (state.mainNav === "playlists" && state.playlistDetailId == null) return;
  const inDetail = state.mainNav === "playlists" && state.playlistDetailId != null;
  const tbody = inDetail ? els.playlistDetailSongList : els.songList;
  if (!tbody) return;
  tbody.innerHTML = "";
  const colspan = inDetail ? 11 : 14;
  const list = state.songs;
  if (!inDetail) updateFrontPaginationUi();
  if (!state.songs.length) {
    tbody.innerHTML = `<tr><td colspan="${colspan}" style="text-align:center;padding:40px;color:var(--sk-muted)">暂无歌曲</td></tr>`;
    if (!inDetail) updateFrontPaginationUi();
    return;
  }
  const pageOffset = inDetail ? 0 : (state.songPage - 1) * state.songPageSize;
  list.forEach((song, index) => {
    const tr = document.createElement("tr");
    tr.dataset.songId = String(song.id);
    if (state.currentIndex >= 0 && state.queue[state.currentIndex]?.id === song.id) tr.classList.add("is-active");
    if (state.selectedSongId != null && songIdEquals(state.selectedSongId, song.id)) tr.classList.add("is-selected");
    tr.innerHTML = inDetail ? songRowPlaylistDetailInnerHtml(song, index) : songRowInnerHtml(song, pageOffset + index);
    tr.addEventListener("click", (e) => {
      if (e.target.closest("[data-stop-row]")) return;
      if (e.target.closest("button") || e.target.closest("input")) return;
      state.selectedSongId = song.id;
      tbody.querySelectorAll("tr").forEach((row) => {
        row.classList.toggle("is-selected", songIdEquals(row.dataset.songId, song.id));
      });
      renderInspector(song);
    });
    tr.addEventListener("dblclick", () => {
      playSong(song.id).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
    });
    if (inDetail) {
      tr.querySelector('[data-role="add"]')?.addEventListener("click", (e) => {
        e.stopPropagation();
        if (e.currentTarget.disabled) return;
        addSongToPlaylist(song.id).catch((err) => showToast(`加入歌单失败: ${err.message}`, "error"));
      });
      tr.querySelector('[data-role="play"]')?.addEventListener("click", (e) => {
        e.stopPropagation();
        if (e.currentTarget.disabled) return;
        playSong(song.id).catch((err) => showToast(`试听失败: ${err.message}`, "error"));
      });
      tr.querySelector('[data-role="download"]')?.addEventListener("click", async (e) => {
        e.stopPropagation();
        await startSongDownloadFlow([song]);
      });
      tr.querySelector('[data-role="delete"]')?.addEventListener("click", (e) => {
        e.stopPropagation();
        removeSongFromCurrentPlaylist(song.id).catch((err) => showToast(`删除失败: ${err.message}`, "error"));
      });
    } else {
      bindFrontRowMoreMenu(tr, song);
    }
    tbody.appendChild(tr);
  });
  scrollActiveSongItemIntoView();
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
  if (state.mainNav === "playlists" && !state.playlistDetailId) renderPlaylistHub();
  showToast("歌单已创建", "success");
}

els.createPlaylistBtn?.addEventListener("click", () => createPlaylist().catch((err) => showToast(`创建歌单失败: ${err.message}`, "error")));
els.prevBtn.addEventListener("click", () => {
  playAdjacentSong(-1).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
});
els.nextBtn.addEventListener("click", () => {
  playAdjacentSong(1).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
});
els.playPlaylistBtn.addEventListener("click", playCurrentPlaylist);
els.playModeSelect?.addEventListener("change", (event) => {
  state.playMode = event.target.value;
  syncTransportDecorations();
});
els.audioPlayer.addEventListener("ended", () => {
  if (state.playMode === "single-loop" && state.currentIndex >= 0 && state.queue[state.currentIndex]) {
    playSong(state.queue[state.currentIndex].id).catch(() => {});
    return;
  }
  playAdjacentSong(1).catch(() => {});
});
els.audioPlayer.addEventListener("timeupdate", () => {
  const a = els.audioPlayer;
  if (!a || !els.playerProgressFill) return;
  const d = a.duration;
  const t = a.currentTime;
  if (Number.isFinite(d) && d > 0) els.playerProgressFill.style.width = `${(t / d) * 100}%`;
  if (els.playerCurrentTime) els.playerCurrentTime.textContent = formatTimeCompact(t);
  syncPlayerLyricLine(t * 1000);
});
els.audioPlayer.addEventListener("loadedmetadata", () => {
  const a = els.audioPlayer;
  if (els.playerDuration && a?.duration) els.playerDuration.textContent = formatTimeCompact(a.duration);
});
els.audioPlayer.addEventListener("play", updatePlayPauseIcon);
els.audioPlayer.addEventListener("pause", updatePlayPauseIcon);
els.playerPlayPauseBtn?.addEventListener("click", () => {
  const a = els.audioPlayer;
  if (!a) return;
  if (!a.src) {
    if (state.queue.length) {
      const i = state.currentIndex >= 0 ? state.currentIndex : 0;
      playSong(state.queue[i].id).catch(() => {});
    }
    return;
  }
  if (a.paused) a.play().catch(() => {});
  else a.pause();
});
els.playerProgressTrack?.addEventListener("click", (e) => {
  const a = els.audioPlayer;
  if (!a || !Number.isFinite(a.duration)) return;
  const rect = els.playerProgressTrack.getBoundingClientRect();
  const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
  a.currentTime = ratio * a.duration;
});
els.playerVolume?.addEventListener("input", () => {
  const a = els.audioPlayer;
  if (!a || !els.playerVolume) return;
  a.volume = Number(els.playerVolume.value) / 100;
});
els.frontUserProfileBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  handleFrontUserMenuItem(() => showToast("个人资料即将接入", "info"));
});
els.frontUserPasswordBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  handleFrontUserMenuItem(() => showToast("修改密码即将接入", "info"));
});
els.frontUserAdminBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  handleFrontUserMenuItem(() => {
    window.location.href = "/admin";
  });
});
els.frontUserLogoutBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  handleFrontUserMenuItem(() => showToast("已退出（演示：刷新页面可重新进入）", "info"));
});
els.frontPageFirstBtn?.addEventListener("click", () => {
  if (state.songPage <= 1) return;
  state.songPage = 1;
  loadSongs({ resetPage: false }).catch((err) => showToast(`加载失败: ${err.message}`, "error"));
});
els.frontPagePrevBtn?.addEventListener("click", () => {
  if (state.songPage > 1) {
    state.songPage -= 1;
    loadSongs({ resetPage: false }).catch((err) => showToast(`加载失败: ${err.message}`, "error"));
  }
});
els.frontPageNextBtn?.addEventListener("click", () => {
  const totalPages = Math.max(1, Math.ceil(state.songListTotal / state.songPageSize));
  if (state.songPage < totalPages) {
    state.songPage += 1;
    loadSongs({ resetPage: false }).catch((err) => showToast(`加载失败: ${err.message}`, "error"));
  }
});
els.frontPageLastBtn?.addEventListener("click", () => {
  const totalPages = Math.max(1, Math.ceil(state.songListTotal / state.songPageSize));
  if (state.songPage >= totalPages) return;
  state.songPage = totalPages;
  loadSongs({ resetPage: false }).catch((err) => showToast(`加载失败: ${err.message}`, "error"));
});
els.frontPageSizeSelect?.addEventListener("change", () => {
  state.songPageSize = Number(els.frontPageSizeSelect.value) || 20;
  loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
});
els.inspectorPlayBtn?.addEventListener("click", () => {
  const song = state.songs.find((s) => songIdEquals(s.id, state.selectedSongId));
  if (!song) return;
  playSong(song.id).catch((err) => showToast(`播放失败: ${err.message}`, "error"));
});
document.querySelectorAll(".sk-nav-item.is-placeholder").forEach((btn) => {
  btn.addEventListener("click", () => showToast("暂未开发", "info"));
});
document.querySelectorAll("[data-sk-nav]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const key = btn.getAttribute("data-sk-nav");
    if (key === "library") {
      state.selectedPlaylistId = null;
      state.playlistDetailId = null;
      state.playlistDetailAllSongs = [];
      state.mainNav = "library";
      updateMainPanels();
      loadSongs()
        .then(() => renderPlaylists())
        .catch((err) => showToast(`加载失败: ${err.message}`, "error"));
      return;
    }
    document.querySelectorAll(".sk-nav-item").forEach((b) => b.classList.remove("is-active"));
    btn.classList.add("is-active");
    showToast("该模块即将推出", "info");
  });
});
document.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    if (state.mainNav === "library") {
      els.libraryKeywordInput?.focus();
    } else {
      els.keywordInput?.focus();
    }
  }
});
wireSearchFieldClear(
  els.libraryKeywordInput,
  els.libraryKeywordClearBtn,
  () => loadSongs().catch((err) => showToast(`查询失败: ${err.message}`, "error")),
  () => updateFrontResetVisibility()
);
els.libraryKeywordInput?.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  loadSongs().catch((err) => showToast(`查询失败: ${err.message}`, "error"));
});
wireSearchFieldClear(
  els.keywordInput,
  els.frontKeywordClearBtn,
  () => {
    if (state.mainNav === "playlists" && !state.playlistDetailId) {
      state.playlistHubFilter = "";
      renderPlaylistHub();
      return;
    }
    if (state.playlistDetailId != null) {
      applyPlaylistDetailFiltersAndSort();
      renderSongList();
      return;
    }
  },
  () => {}
);
els.keywordInput.addEventListener("input", () => {
  if (state.mainNav !== "playlists") return;
  if (state.playlistDetailId != null) {
    applyPlaylistDetailFiltersAndSort();
    renderSongList();
  } else {
    state.playlistHubFilter = els.keywordInput.value;
    renderPlaylistHub();
  }
});
els.keywordInput.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  if (state.mainNav === "playlists") {
    if (state.playlistDetailId != null) {
      applyPlaylistDetailFiltersAndSort();
      renderSongList();
    } else {
      state.playlistHubFilter = els.keywordInput.value;
      renderPlaylistHub();
    }
    return;
  }
});
els.resetFrontFiltersBtn?.addEventListener("click", () => resetFrontSongListFilters());
els.frontToggleFilterBtn?.addEventListener("click", () => {
  if (!els.frontFilterSection) return;
  const willOpen = els.frontFilterSection.classList.contains("hidden");
  const activeMenu = getActiveSearchableSelectMenu();
  if (!willOpen && activeMenu && els.frontFilterSection.contains(activeMenu)) {
    clearActiveSearchableSelectMenu();
  }
  setFrontFiltersPanelOpen(willOpen);
});
frontFilterSelectEls().forEach((el) => {
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

document.addEventListener("click", (e) => {
  closeActiveSearchableSelectMenuOnOutsideClick(e.target);
  if (els.frontUserMenu && !els.frontUserMenu.classList.contains("hidden")) {
    const inMenu = els.frontUserMenu.contains(e.target);
    const onBtn = els.frontUserMenuBtn?.contains(e.target);
    if (!inMenu && !onBtn) setFrontUserMenuOpen(false);
  }
  closeAllFrontRowMoreMenus();
});

els.songList?.closest(".studio-library-table-wrap")?.addEventListener("scroll", () => closeAllFrontRowMoreMenus(), { passive: true });

document.getElementById("btnBackPlaylistDetail")?.addEventListener("click", () => closePlaylistDetail());
document.getElementById("playlistSortSelect")?.addEventListener("change", (e) => {
  state.playlistSort = e.target.value;
  renderPlaylistHub();
});
document.getElementById("psViewGridBtn")?.addEventListener("click", () => {
  state.playlistViewGrid = true;
  document.getElementById("psViewGridBtn")?.classList.add("is-active");
  document.getElementById("psViewListBtn")?.classList.remove("is-active");
  document.getElementById("playlistCardGrid")?.classList.remove("ps-list-view");
});
document.getElementById("psViewListBtn")?.addEventListener("click", () => {
  state.playlistViewGrid = false;
  document.getElementById("psViewListBtn")?.classList.add("is-active");
  document.getElementById("psViewGridBtn")?.classList.remove("is-active");
  document.getElementById("playlistCardGrid")?.classList.add("ps-list-view");
});
document.querySelectorAll(".ps-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".ps-tab").forEach((t) => t.classList.remove("is-active"));
    tab.classList.add("is-active");
    showToast("筛选项即将与后端标签打通", "info");
  });
});
document.getElementById("btnPlaylistSpaceAi")?.addEventListener("click", () => {
  showToast("AI 生成歌单即将接入工作流", "info");
});
document.getElementById("btnDetailImportMusic")?.addEventListener("click", () => {
  window.location.href = "/admin";
});
document.getElementById("btnDetailNewPlaylist")?.addEventListener("click", () => {
  createPlaylist().catch((err) => showToast(`创建歌单失败: ${err.message}`, "error"));
});
document.getElementById("pdPlayAllBtn")?.addEventListener("click", () => playCurrentPlaylist());
document.getElementById("pdEditBtn")?.addEventListener("click", async () => {
  const id = state.playlistDetailId;
  if (id == null) return;
  const pl = state.playlists.find((p) => songIdEquals(p.id, id));
  const name = await openModal({
    title: "修改歌单",
    message: "请输入新的歌单名称。",
    withInput: true,
    confirmText: "保存",
    defaultValue: pl?.name || "",
  });
  if (!name || !name.trim()) return;
  await request(`/playlists/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: name.trim() }) });
  await loadPlaylists();
  await refreshPlaylistDetailData();
  showToast("已保存", "success");
});
document.getElementById("pdAddSongsBtn")?.addEventListener("click", () => {
  showToast("请在「音乐库」中将曲目加入歌单", "info");
  state.playlistDetailId = null;
  state.playlistDetailAllSongs = [];
  state.selectedPlaylistId = null;
  state.mainNav = "library";
  updateMainPanels();
  loadSongs().catch((err) => showToast(err.message, "error"));
  syncNavForPlaylistState();
});
document.getElementById("pdDownloadBtn")?.addEventListener("click", () => showToast("打包下载即将接入", "info"));
document.getElementById("pdMoreBtn")?.addEventListener("click", () => showToast("更多操作菜单即将接入", "info"));
document.getElementById("pdSongFilterInput")?.addEventListener("input", () => {
  applyPlaylistDetailFiltersAndSort();
  renderSongList();
});
document.getElementById("pdSongSortSelect")?.addEventListener("change", () => {
  applyPlaylistDetailFiltersAndSort();
  renderSongList();
});
document.querySelectorAll(".pd-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".pd-tab").forEach((t) => t.classList.remove("is-active"));
    tab.classList.add("is-active");
    const k = tab.getAttribute("data-pd-tab");
    const songsPanel = document.getElementById("pdPanelSongs");
    const ph = document.getElementById("pdPanelPlaceholder");
    const showSongs = k === "songs";
    songsPanel?.classList.toggle("hidden", !showSongs);
    ph?.classList.toggle("hidden", showSongs);
  });
});
document.getElementById("pdSongSelectAll")?.addEventListener("change", (e) => {
  const on = e.target.checked;
  document.querySelectorAll("#playlistDetailSongList .song-row-check").forEach((c) => {
    c.checked = on;
  });
});

async function initPage() {
  try {
    if (els.audioPlayer && els.playerVolume) {
      els.audioPlayer.volume = Number(els.playerVolume.value) / 100;
    }
    syncTransportDecorations();
    updatePlayPauseIcon();
    await loadFilterOptions();
    await loadLibraryStats();
    await loadPlaylists();
    await loadSongs();
    renderPlaylists();
    updateMainPanels();
    syncNavForPlaylistState();
  } catch (err) {
    if (els.songList) els.songList.innerHTML = `<tr><td colspan="14" style="text-align:center;padding:24px">加载失败: ${escapeHtml(err.message)}</td></tr>`;
    showToast(`前台初始化失败: ${err.message}`, "error");
  }
}

document.getElementById("songSelectAll")?.addEventListener("change", (e) => {
  const on = e.target.checked;
  document.querySelectorAll(".song-row-check").forEach((c) => {
    c.checked = on;
  });
});
document.querySelectorAll(".studio-inspector-tabs button").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".studio-inspector-tabs button").forEach((t) => t.classList.remove("is-active"));
    tab.classList.add("is-active");
    state.inspectorTab = tab.dataset.tab || "detail";
    const song =
      state.songs.find((s) => s.id === state.selectedSongId) ||
      state.queue.find((s) => s.id === state.selectedSongId);
    if (song) renderInspectorPanel(song);
  });
});

applyAppVersion();
initFrontSidebarCollapse();
initFrontUserMenu();
initPlayerLyricsToggle();
initPage();
