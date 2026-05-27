import { applyAppVersion } from "./version.js";
import { findLyricLineAtTime, loadSongLyricsViaRequest, LYRIC_PLACEHOLDER } from "./lrc.js";
import {
  closeActiveSearchableSelectMenuOnOutsideClick,
  ensureSearchableSelect,
  filterDropdownSelectedRawValues,
  fuzzyMatchName,
  refreshSearchableSelectOptions,
  syncSearchableSelectTrigger,
} from "./searchable-select.js";

const state = {
  songs: [],
  tags: [],
  languages: [],
  genres: [],
  people: [],
  filters: null,
  editingSongId: null,
  editingCurrentFileId: null,
  variantFileActionsSetup: false,
  sortBy: "created_at",
  sortOrder: "desc",
  playQueue: [],
  currentPlayIndex: -1,
  playMode: "list-loop",
  currentAdminPage: "music",
  createModalType: null,
  createEditData: null,
  editModalType: null,
  editModalId: null,
  deleteModalType: null,
  deleteModalId: null,
  batchDeleteIds: [],
  batchDeleteManager: null,
  scanProgressTimer: null,
  selectedSongs: new Set(),
  /** 歌曲列表行选择的播放/下载格式，空字符串表示自动（服务端推荐） */
  songFormatPreference: {},
  lyricLines: [],
  lyricSongId: null,
  lyricContent: "",
  peopleSortBy: "name",
  peopleSortOrder: "asc",
  tagSortBy: "name",
  tagSortOrder: "asc",
  languageSortBy: "name",
  languageSortOrder: "asc",
  genreSortBy: "name",
  genreSortOrder: "asc",
  selectedPeople: new Set(),
  selectedTags: new Set(),
  selectedLanguages: new Set(),
  selectedGenres: new Set(),
  activeSongId: null,
  playingSongId: null,
  songPage: 1,
  songPageSize: 20,
  songListTotal: 0,
  songLibraryTotal: 0,
  quickFilterLeads: [],
  quickFilterLyricists: [],
  quickFilterComposers: [],
  quickFilterTags: [],
  quickFilterFormats: [],
  quickFilterLanguages: [],
  quickFilterGenres: [],
};

const ADMIN_QUICK_FILTER_SELECTS = () =>
  [
    els.filterLeadQuick,
    els.filterLyricistQuick,
    els.filterComposerQuick,
    els.filterTagQuick,
    els.filterFormatQuick,
    els.filterLanguageQuick,
    els.filterGenreQuick,
  ].filter(Boolean);

const els = {
  scanBtn: document.querySelector("#scanBtn"),
  addSongsBtn: document.querySelector("#addSongsBtn"),
  songFilePicker: document.querySelector("#songFilePicker"),
  directoryPicker: document.querySelector("#directoryPicker"),
  scanSummary: document.querySelector("#scanSummary"),
  scanProgressWrap: document.querySelector("#scanProgressWrap"),
  scanProgressText: document.querySelector("#scanProgressText"),
  scanProgressStats: document.querySelector("#scanProgressStats"),
  scanProgressFill: document.querySelector("#scanProgressFill"),
  scanElapsedTime: document.querySelector("#scanElapsedTime"),
  scanEstimatedTime: document.querySelector("#scanEstimatedTime"),
  adminNavMusic: document.querySelector("#adminNavMusic"),
  adminNavPeople: document.querySelector("#adminNavPeople"),
  adminNavTags: document.querySelector("#adminNavTags"),
  adminNavLanguage: document.querySelector("#adminNavLanguage"),
  goFrontendBtn: document.querySelector("#goFrontendBtn"),
  adminUserAvatarBtn: document.querySelector("#adminUserAvatarBtn"),
  adminUserMenu: document.querySelector("#adminUserMenu"),
  keywordInput: document.querySelector("#keywordInput"),
  keywordClearBtn: document.querySelector("#keywordClearBtn"),
  resetSongFiltersBtn: document.querySelector("#resetSongFiltersBtn"),
  toggleFilterBtn: document.querySelector("#toggleFilterBtn"),
  admFiltersPanel: document.querySelector("#admFiltersPanel"),
  genreInput: document.querySelector("#genreInput"),
  scanSummary: document.querySelector("#scanSummary"),
  songTableBody: document.querySelector("#songTableBody"),
  sortButtons: Array.from(document.querySelectorAll(".sort-btn")),
  selectAllSongs: document.querySelector("#selectAllSongs"),
  batchMergeDuplicatesBtn: document.querySelector("#batchMergeDuplicatesBtn"),
  batchMergeSelectedBtn: document.querySelector("#batchMergeSelectedBtn"),
  batchDeleteBtn: document.querySelector("#batchDeleteBtn"),
  batchDownloadBtn: document.querySelector("#batchDownloadBtn"),
  relocateSelectedStorageBtn: document.querySelector("#relocateSelectedStorageBtn"),
  relocateProgressWrap: document.querySelector("#relocateProgressWrap"),
  relocateProgressText: document.querySelector("#relocateProgressText"),
  relocateProgressStats: document.querySelector("#relocateProgressStats"),
  relocateProgressFill: document.querySelector("#relocateProgressFill"),
  toastContainer: document.querySelector("#toastContainer"),
  modalOverlay: document.querySelector("#modalOverlay"),
  modalTitle: document.querySelector("#modalTitle"),
  modalMessage: document.querySelector("#modalMessage"),
  modalInputWrap: document.querySelector("#modalInputWrap"),
  modalInput: document.querySelector("#modalInput"),
  modalCloseBtn: document.querySelector("#modalCloseBtn"),
  modalCancelBtn: document.querySelector("#modalCancelBtn"),
  modalConfirmBtn: document.querySelector("#modalConfirmBtn"),
  editOverlay: document.querySelector("#editOverlay"),
  adminEditPanel: document.querySelector("#adminEditPanel"),
  pagePrevBtn: document.querySelector("#pagePrevBtn"),
  pageNextBtn: document.querySelector("#pageNextBtn"),
  pageNumbers: document.querySelector("#pageNumbers"),
  pageSizeSelect: document.querySelector("#pageSizeSelect"),
  songListTotalLabel: document.querySelector("#songListTotalLabel"),
  filterLeadQuick: document.querySelector("#filterLeadQuick"),
  filterLyricistQuick: document.querySelector("#filterLyricistQuick"),
  filterComposerQuick: document.querySelector("#filterComposerQuick"),
  filterTagQuick: document.querySelector("#filterTagQuick"),
  filterFormatQuick: document.querySelector("#filterFormatQuick"),
  filterLanguageQuick: document.querySelector("#filterLanguageQuick"),
  filterGenreQuick: document.querySelector("#filterGenreQuick"),
  editFormatsReadonly: document.querySelector("#editFormatsReadonly"),
  durationDisplay: document.querySelector("#durationDisplay"),
  editLyricName: document.querySelector("#editLyricName"),
  editLyricReplaceBtn: document.querySelector("#editLyricReplaceBtn"),
  editLyricFileInput: document.querySelector("#editLyricFileInput"),
  logoutBtn: document.querySelector("#logoutBtn"),
  statSongCount: document.querySelector("#statSongCount"),
  statArtistCount: document.querySelector("#statArtistCount"),
  statAlbumCount: document.querySelector("#statAlbumCount"),
  statFixCount: document.querySelector("#statFixCount"),
  statAiTaskPct: document.querySelector("#statAiTaskPct"),
  statAiTaskBar: document.querySelector("#statAiTaskBar"),
  metadataForm: document.querySelector("#metadataForm"),
  titleInput: document.querySelector("#titleInput"),
  leadArtistInput: document.querySelector("#leadArtistInput"),
  lyricistInput: document.querySelector("#lyricistInput"),
  composerInput: document.querySelector("#composerInput"),
  albumInput: document.querySelector("#albumInput"),
  filmTvInput: document.querySelector("#filmTvInput"),
  languageInput: document.querySelector("#languageInput"),
  releaseDateInput: document.querySelector("#releaseDateInput"),
  tagInput: document.querySelector("#tagInput"),
  variantList: document.querySelector("#variantList"),
  editDrawerBackdrop: document.querySelector("#editDrawerBackdrop"),
  editCloseBtn: document.querySelector("#editCloseBtn"),
  editCancelBtn: document.querySelector("#editCancelBtn"),
  songAddFileBtn: document.querySelector("#songAddFileBtn"),
  songAddFileInput: document.querySelector("#songAddFileInput"),
  tagSearchInput: document.querySelector("#tagSearchInput"),
  tagSearchClearBtn: document.querySelector("#tagSearchClearBtn"),
  tagNewBtn: document.querySelector("#tagNewBtn"),
  tagManagerList: document.querySelector("#tagManagerList"),
  tagTableBody: document.querySelector("#tagTableBody"),
  peopleSearchInput: document.querySelector("#peopleSearchInput"),
  peopleSearchClearBtn: document.querySelector("#peopleSearchClearBtn"),
  peopleNewBtn: document.querySelector("#peopleNewBtn"),
  peopleBatchDeleteBtn: document.querySelector("#peopleBatchDeleteBtn"),
  selectAllPeople: document.querySelector("#selectAllPeople"),
  peopleManagerList: document.querySelector("#peopleManagerList"),
  peopleTableBody: document.querySelector("#peopleTableBody"),
  languageSearchInput: document.querySelector("#languageSearchInput"),
  languageSearchClearBtn: document.querySelector("#languageSearchClearBtn"),
  languageNewBtn: document.querySelector("#languageNewBtn"),
  languageBatchDeleteBtn: document.querySelector("#languageBatchDeleteBtn"),
  selectAllLanguages: document.querySelector("#selectAllLanguages"),
  languageManagerList: document.querySelector("#languageManagerList"),
  languageTableBody: document.querySelector("#languageTableBody"),
  genreSearchInput: document.querySelector("#genreSearchInput"),
  genreSearchClearBtn: document.querySelector("#genreSearchClearBtn"),
  genreNewBtn: document.querySelector("#genreNewBtn"),
  genreBatchDeleteBtn: document.querySelector("#genreBatchDeleteBtn"),
  selectAllGenres: document.querySelector("#selectAllGenres"),
  genreManagerList: document.querySelector("#genreManagerList"),
  genreTableBody: document.querySelector("#genreTableBody"),
  tagBatchDeleteBtn: document.querySelector("#tagBatchDeleteBtn"),
  selectAllTags: document.querySelector("#selectAllTags"),
  createOverlay: document.querySelector("#createOverlay"),
  createModalTitle: document.querySelector("#createModalTitle"),
  createFormBody: document.querySelector("#createFormBody"),
  createForm: document.querySelector("#createForm"),
  createCloseBtn: document.querySelector("#createCloseBtn"),
  createCancelBtn: document.querySelector("#createCancelBtn"),
  createSubmitBtn: document.querySelector("#createSubmitBtn"),
  editModalTitle: document.querySelector("#editModalTitle"),
  editFormBody: document.querySelector("#editFormBody"),
  itemEditOverlay: document.querySelector("#itemEditOverlay"),
  itemEditCloseBtn: document.querySelector("#itemEditCloseBtn"),
  itemEditCancelBtn: document.querySelector("#itemEditCancelBtn"),
  itemEditForm: document.querySelector("#itemEditForm"),
  deleteOverlay: document.querySelector("#deleteOverlay"),
  deleteMessage: document.querySelector("#deleteMessage"),
  deleteCloseBtn: document.querySelector("#deleteCloseBtn"),
  deleteCancelBtn: document.querySelector("#deleteCancelBtn"),
  deleteConfirmBtn: document.querySelector("#deleteConfirmBtn"),
  skippedOverlay: document.querySelector("#skippedOverlay"),
  skippedFilesTableBody: document.querySelector("#skippedFilesTableBody"),
  skippedCloseBtn: document.querySelector("#skippedCloseBtn"),
  skippedDismissBtn: document.querySelector("#skippedDismissBtn"),
  mergeTargetOverlay: document.querySelector("#mergeTargetOverlay"),
  mergeTargetList: document.querySelector("#mergeTargetList"),
  mergeTargetCloseBtn: document.querySelector("#mergeTargetCloseBtn"),
  mergeTargetCancelBtn: document.querySelector("#mergeTargetCancelBtn"),
  mergeTargetConfirmBtn: document.querySelector("#mergeTargetConfirmBtn"),
  downloadFormatsOverlay: document.querySelector("#downloadFormatsOverlay"),
  downloadFormatsHint: document.querySelector("#downloadFormatsHint"),
  downloadFormatsList: document.querySelector("#downloadFormatsList"),
  downloadFormatsCloseBtn: document.querySelector("#downloadFormatsCloseBtn"),
  downloadFormatsCancelBtn: document.querySelector("#downloadFormatsCancelBtn"),
  downloadFormatsConfirmBtn: document.querySelector("#downloadFormatsConfirmBtn"),
  adminPrevBtn: document.querySelector("#adminPrevBtn"),
  adminNextBtn: document.querySelector("#adminNextBtn"),
  adminPlayModeSelect: document.querySelector("#adminPlayModeSelect"),
  adminAudioPlayer: document.querySelector("#adminAudioPlayer"),
  adminPlayerPlayPauseBtn: document.querySelector("#adminPlayerPlayPauseBtn"),
  adminPlayerBarTitle: document.querySelector("#adminPlayerBarTitle"),
  adminPlayerBarArtist: document.querySelector("#adminPlayerBarArtist"),
  adminPlayerNextHint: document.querySelector("#adminPlayerNextHint"),
  adminPlayerProgressTrack: document.querySelector("#adminPlayerProgressTrack"),
  adminPlayerProgressFill: document.querySelector("#adminPlayerProgressFill"),
  adminPlayerCurrentTime: document.querySelector("#adminPlayerCurrentTime"),
  adminPlayerDuration: document.querySelector("#adminPlayerDuration"),
  adminPlayerVolume: document.querySelector("#adminPlayerVolume"),
  adminPlayerLyricLine: document.querySelector("#adminPlayerLyricLine"),
};

const modalState = { resolver: null };
let activeMultiSelect = null;
let adminAudioPlayGeneration = 0;
let lastAdminPlayerLyricText = "";

async function loadAdminSongLyrics(songId) {
  if (!songId) {
    state.lyricLines = [];
    state.lyricSongId = null;
    state.lyricContent = "";
    syncAdminPlayerLyricLine(0);
    return;
  }
  const data = await loadSongLyricsViaRequest(request, songId);
  state.lyricSongId = songId;
  if (!data) {
    state.lyricLines = [];
    state.lyricContent = "";
    syncAdminPlayerLyricLine(0);
    return;
  }
  state.lyricLines = data.lines;
  state.lyricContent = data.content;
  syncAdminPlayerLyricLine((els.adminAudioPlayer?.currentTime || 0) * 1000);
}

function syncAdminPlayerLyricLine(timeMs) {
  if (!els.adminPlayerLyricLine) return;
  if (!state.lyricLines?.length || state.lyricSongId == null) {
    if (lastAdminPlayerLyricText !== LYRIC_PLACEHOLDER) {
      els.adminPlayerLyricLine.textContent = LYRIC_PLACEHOLDER;
      lastAdminPlayerLyricText = LYRIC_PLACEHOLDER;
    }
    return;
  }
  const text = findLyricLineAtTime(state.lyricLines, timeMs);
  const display = text || "···";
  if (display !== lastAdminPlayerLyricText) {
    els.adminPlayerLyricLine.textContent = display;
    lastAdminPlayerLyricText = display;
  }
}

async function uploadLyricForSong(songId, file) {
  const fd = new FormData();
  fd.append("file", file);
  return request(`/songs/${songId}/lyrics`, { method: "POST", body: fd });
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
  const text = await res.text();
  if (!res.ok) {
    let msg = (text && text.trim()) || `Request failed: ${res.status}`;
    try {
      const j = JSON.parse(text);
      if (typeof j.detail === "string") msg = j.detail;
      else if (Array.isArray(j.detail))
        msg = j.detail.map((e) => (e && e.msg ? e.msg : JSON.stringify(e))).join("；");
      else if (j.detail != null && typeof j.detail === "object") msg = JSON.stringify(j.detail);
    } catch (_) {
      /* 非 JSON 时使用原文本 */
    }
    throw new Error(msg);
  }
  if (res.status === 204) return null;
  if (!text || !text.trim()) return null;
  return JSON.parse(text);
}

function showToast(message, type = "info", durationMs) {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  els.toastContainer.appendChild(toast);
  const ms =
    durationMs != null
      ? durationMs
      : type === "error" && String(message).length > 140
        ? 11000
        : 2800;
  setTimeout(() => toast.remove(), ms);
}

/** 搜索框内一键清空；可选 onInputSync（每次输入同步 UI）；清空后 onCleared */
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

function adminMusicHasActiveFilters() {
  const kw = (els.keywordInput?.value || "").trim();
  if (kw) return true;
  return !!(
    state.quickFilterLeads.length ||
    state.quickFilterLyricists.length ||
    state.quickFilterComposers.length ||
    state.quickFilterTags.length ||
    state.quickFilterFormats.length ||
    state.quickFilterLanguages.length ||
    state.quickFilterGenres.length
  );
}

function updateAdminMusicResetVisibility() {
  if (!els.resetSongFiltersBtn) return;
  els.resetSongFiltersBtn.classList.toggle("hidden", !adminMusicHasActiveFilters());
}

function adminGlobalIndexFromLocal(localIdx) {
  return (state.songPage - 1) * state.songPageSize + localIdx;
}

function adminLocalIndexFromGlobal(globalIdx) {
  return globalIdx % state.songPageSize;
}

function adminPageFromGlobal(globalIdx) {
  return Math.floor(globalIdx / state.songPageSize) + 1;
}

const ADMIN_SCROLL_TABLE_HEAD_GAP = 4;

function scrollAdminPlayingRowIntoView() {
  const tbody = els.songTableBody;
  if (!tbody) return;
  const active = tbody.querySelector("tr.is-playing");
  if (!active) return;
  requestAnimationFrame(() => {
    const wrap = tbody.closest(".adm-table-scroll");
    if (!wrap) return;
    const thead = wrap.querySelector("thead");
    const theadH = (thead?.offsetHeight ?? 0) + ADMIN_SCROLL_TABLE_HEAD_GAP;
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

async function ensureAdminPageForGlobalIndex(globalIdx) {
  const page = adminPageFromGlobal(globalIdx);
  if (page !== state.songPage) {
    state.songPage = page;
    await loadSongs();
  }
}

async function playAdminSongAtGlobalIndex(globalIdx) {
  await ensureAdminPageForGlobalIndex(globalIdx);
  state.playQueue = state.songs.slice();
  const localIdx = adminLocalIndexFromGlobal(globalIdx);
  const song = state.playQueue[localIdx];
  if (!song) {
    showToast("无法定位歌曲", "error");
    return;
  }
  await playSongInAdmin(song.id, preferredFormatForQueueItem(song), localIdx);
}

async function playAdminAdjacentSong(direction) {
  const total = state.songListTotal;
  if (total <= 0) return;
  state.playQueue = state.songs.slice();
  if (!state.playQueue.length) return;

  if (state.playMode === "shuffle") {
    const idx = Math.floor(Math.random() * state.playQueue.length);
    const song = state.playQueue[idx];
    await playSongInAdmin(song.id, preferredFormatForQueueItem(song), idx);
    return;
  }
  if (state.playMode === "single-loop" && state.currentPlayIndex >= 0) {
    const song = state.playQueue[state.currentPlayIndex];
    if (song) await playSongInAdmin(song.id, preferredFormatForQueueItem(song), state.currentPlayIndex);
    return;
  }

  if (state.currentPlayIndex < 0) {
    const idx = adminFindNextPlayableIndex(-1);
    if (idx >= 0) {
      const song = state.playQueue[idx];
      await playSongInAdmin(song.id, preferredFormatForQueueItem(song), idx);
    }
    return;
  }

  let globalIdx = adminGlobalIndexFromLocal(state.currentPlayIndex);
  let nextGlobal = globalIdx + direction;
  if (state.playMode === "list-loop") {
    if (nextGlobal < 0) nextGlobal = total - 1;
    if (nextGlobal >= total) nextGlobal = 0;
  } else if (nextGlobal < 0 || nextGlobal >= total) {
    return;
  }

  await playAdminSongAtGlobalIndex(nextGlobal);
}

function adminNextPlayIndex() {
  if (!state.playQueue.length) return -1;
  if (state.playMode === "single-loop") return state.currentPlayIndex;
  if (state.playMode === "shuffle") return Math.floor(Math.random() * state.playQueue.length);
  if (state.currentPlayIndex < state.playQueue.length - 1) return state.currentPlayIndex + 1;
  if (state.playMode === "list-loop") return 0;
  // sequence：最后一首后不循环
  return -1;
}

function adminPrevPlayIndex() {
  if (!state.playQueue.length) return -1;
  if (state.playMode === "single-loop") return state.currentPlayIndex;
  if (state.playMode === "shuffle") return Math.floor(Math.random() * state.playQueue.length);
  if (state.currentPlayIndex > 0) return state.currentPlayIndex - 1;
  if (state.playMode === "list-loop") return state.playQueue.length - 1;
  return -1;
}

/** 非单曲模式下跳过失败曲目；若下一索引仍为当前曲则顺序进一位 */
function adminNextIndexAfterPlaybackFailure() {
  const len = state.playQueue.length;
  if (len <= 1) return -1;
  const normal = adminNextPlayIndex();
  if (normal !== state.currentPlayIndex) return normal;
  return (state.currentPlayIndex + 1) % len;
}

function adminSongIdEquals(a, b) {
  return a === b || String(a) === String(b);
}

/** 从 afterIdx 之后找下一首可试听曲目；afterIdx 为 -1 时从队列头扫描 */
function adminFindNextPlayableIndex(afterIdx) {
  const q = state.playQueue;
  const len = q.length;
  if (!len) return -1;
  for (let step = 1; step <= len; step++) {
    const i = ((afterIdx >= 0 ? afterIdx : -1) + step) % len;
    if (songHasWebPlayableAudio(q[i])) return i;
  }
  return -1;
}

function formatAdminTimeCompact(sec) {
  if (!sec || !Number.isFinite(sec)) return "0:00";
  const s = Math.floor(sec % 60);
  const m = Math.floor(sec / 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

function updateAdminPlayerShell(song, playInfo = null) {
  const title = song?.title || "暂无播放";
  const artist = song?.lead_artist || "—";
  const fmt = playInfo?.selected_format ? String(playInfo.selected_format).toUpperCase() : "";
  if (els.adminPlayerBarTitle) els.adminPlayerBarTitle.textContent = title;
  if (els.adminPlayerBarArtist) {
    els.adminPlayerBarArtist.textContent = fmt ? `${artist} · ${fmt}` : artist;
  }
}

function updateAdminPlayPauseIcon() {
  const a = els.adminAudioPlayer;
  const btn = els.adminPlayerPlayPauseBtn;
  if (!btn || !a) return;
  btn.textContent = a.paused ? "▶" : "⏸";
}

function updateAdminNextTrackHint() {
  if (!els.adminPlayerNextHint) return;
  const idx = adminNextPlayIndex();
  if (idx < 0 || !state.playQueue[idx]) {
    els.adminPlayerNextHint.textContent = "";
    return;
  }
  const n = state.playQueue[idx];
  els.adminPlayerNextHint.textContent = `下一首：${n.title || "—"} · ${n.lead_artist || ""}`;
}

function syncAdminTransportDecorations() {
  if (els.adminPlayModeSelect) els.adminPlayModeSelect.value = state.playMode;
}

function initAdminStudioPlayer() {
  const audio = els.adminAudioPlayer;
  if (!audio || audio.dataset.adminStudioBound === "1") return;
  audio.dataset.adminStudioBound = "1";
  if (els.adminPlayerVolume) audio.volume = Number(els.adminPlayerVolume.value) / 100;
  syncAdminTransportDecorations();
  updateAdminPlayPauseIcon();
  audio.addEventListener("timeupdate", () => {
    if (!els.adminPlayerProgressFill) return;
    const d = audio.duration;
    const t = audio.currentTime;
    if (Number.isFinite(d) && d > 0) els.adminPlayerProgressFill.style.width = `${(t / d) * 100}%`;
    if (els.adminPlayerCurrentTime) els.adminPlayerCurrentTime.textContent = formatAdminTimeCompact(t);
    syncAdminPlayerLyricLine(t * 1000);
  });
  audio.addEventListener("loadedmetadata", () => {
    if (els.adminPlayerDuration && Number.isFinite(audio.duration)) {
      els.adminPlayerDuration.textContent = formatAdminTimeCompact(audio.duration);
    }
  });
  audio.addEventListener("play", updateAdminPlayPauseIcon);
  audio.addEventListener("pause", updateAdminPlayPauseIcon);
  els.adminPlayerPlayPauseBtn?.addEventListener("click", () => {
    if (!audio.src) {
      if (state.playQueue.length) {
        const i = state.currentPlayIndex >= 0 ? state.currentPlayIndex : 0;
        const item = state.playQueue[i];
        if (item) {
          playSongInAdmin(item.id, preferredFormatForQueueItem(item), i).catch((err) =>
            showToast(`播放失败: ${err.message || err}`, "error")
          );
        }
      }
      return;
    }
    if (audio.paused) audio.play().catch(() => showToast("无法播放", "error"));
    else audio.pause();
  });
  els.adminPlayerProgressTrack?.addEventListener("click", (e) => {
    if (!Number.isFinite(audio.duration)) return;
    const rect = els.adminPlayerProgressTrack.getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
    audio.currentTime = ratio * audio.duration;
  });
  els.adminPlayerVolume?.addEventListener("input", () => {
    audio.volume = Number(els.adminPlayerVolume.value) / 100;
  });
}

async function playSongInAdmin(songId, preferredFormat = "", queueIndex = -1, failureAttempt = 0) {
  if (!state.songs.some((s) => adminSongIdEquals(s.id, songId))) {
    showToast("当前页未找到该歌曲", "warning");
    return;
  }
  state.playQueue = state.songs.slice();
  const queueLen = state.playQueue.length;
  if (queueLen && failureAttempt >= queueLen) {
    showToast("列表中的歌曲均无法播放", "error");
    return;
  }
  const rowSong = state.playQueue.find((s) => adminSongIdEquals(s.id, songId));
  if (rowSong && !songHasWebPlayableAudio(rowSong)) {
    let badIdx = queueIndex >= 0 ? queueIndex : state.playQueue.findIndex((s) => adminSongIdEquals(s.id, songId));
    if (badIdx < 0) badIdx = state.songs.findIndex((s) => adminSongIdEquals(s.id, songId));
    if (badIdx < 0) {
      const idx = adminFindNextPlayableIndex(state.currentPlayIndex);
      if (idx >= 0) {
        showToast("当前曲目无可播格式，已跳过", "warning");
        const item = state.playQueue[idx];
        playSongInAdmin(item.id, preferredFormatForQueueItem(item), idx, failureAttempt + 1).catch(() => {});
      } else {
        showToast("列表中的歌曲均无法播放", "error");
      }
      return;
    }
    state.currentPlayIndex = badIdx;
    const idx = adminNextIndexAfterPlaybackFailure();
    if (idx >= 0 && state.playQueue[idx] && songHasWebPlayableAudio(state.playQueue[idx])) {
      showToast("当前曲目无可播格式，已跳过", "warning");
      const item = state.playQueue[idx];
      playSongInAdmin(item.id, preferredFormatForQueueItem(item), idx, failureAttempt + 1).catch(() => {});
    } else {
      const fallback = adminFindNextPlayableIndex(badIdx);
      if (fallback >= 0) {
        showToast("当前曲目无可播格式，已跳过", "warning");
        const item = state.playQueue[fallback];
        playSongInAdmin(item.id, preferredFormatForQueueItem(item), fallback, failureAttempt + 1).catch(() => {});
      } else {
        showToast("列表中的歌曲均无法播放", "error");
      }
    }
    return;
  }
  const params = new URLSearchParams();
  if (preferredFormat) params.set("preferred_format", preferredFormat);
  const url = `/songs/${songId}/play${params.toString() ? "?" + params.toString() : ""}`;
  const playInfo = await request(url);
  const localIdx = queueIndex >= 0 ? queueIndex : state.playQueue.findIndex((s) => adminSongIdEquals(s.id, songId));
  state.currentPlayIndex = localIdx;
  state.playingSongId = songId;
  const song = state.playQueue[localIdx] || { title: "未知歌曲" };
  renderSongs();
  scrollAdminPlayingRowIntoView();
  const audio = els.adminAudioPlayer;
  if (!audio) {
    updateAdminPlayerShell(song, playInfo);
    return;
  }
  const streamSrc = resolveMediaSrc(playInfo.stream_url);
  adminAudioPlayGeneration += 1;
  const gen = adminAudioPlayGeneration;

  const skipToNext = (message) => {
    if (gen !== adminAudioPlayGeneration) return;
    if (state.playMode === "single-loop") {
      showToast("当前曲目无法播放", "error");
      return;
    }
    const idx = adminNextIndexAfterPlaybackFailure();
    if (idx >= 0 && state.playQueue[idx]) {
      showToast(message || "当前曲目无法播放，已跳过", "warning");
      const item = state.playQueue[idx];
      playSongInAdmin(item.id, preferredFormatForQueueItem(item), idx, failureAttempt + 1).catch(() => {});
    } else {
      showToast("播放失败", "error");
    }
  };

  const onErr = () => {
    audio.removeEventListener("error", onErr);
    if (gen !== adminAudioPlayGeneration) return;
    skipToNext("当前曲目无法播放，已跳过");
  };
  audio.addEventListener("error", onErr, { once: true });

  audio.src = streamSrc;
  updateAdminPlayerShell(song, playInfo);
  updateAdminNextTrackHint();
  loadAdminSongLyrics(songId).catch(() => {});

  try {
    await audio.play();
    updateAdminPlayPauseIcon();
  } catch (_err) {
    audio.removeEventListener("error", onErr);
    if (gen !== adminAudioPlayGeneration) return;
    skipToNext("当前曲目无法播放，已跳过");
  }
}

function closeModal(result = null) {
  els.modalOverlay.classList.add("hidden");
  const resolver = modalState.resolver;
  modalState.resolver = null;
  if (resolver) resolver(result);
}

function showAdminPage(page) {
  state.currentAdminPage = page;
  document.querySelectorAll(".admin-page").forEach((el) => el.classList.add("hidden"));
  document.querySelectorAll(".admin-nav-item, .adm-nav-item").forEach((el) => {
    el.classList.remove("active", "is-active");
  });
  const pageEl = document.getElementById(`admin-page-${page}`);
  const navEl = document.querySelector(`.admin-nav-item[data-page="${page}"], .adm-nav-item[data-page="${page}"]`);
  if (pageEl) pageEl.classList.remove("hidden");
  if (navEl) {
    navEl.classList.add("active", "is-active");
  }
  if (page === "music") {
    updateAdminMusicResetVisibility();
    updateAdminStats();
  } else {
    closeEditModal();
  }
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

function songAdminStatus(song) {
  const variants = song.file_variants || [];
  const hasFile = variants.length > 0 || (song.formats || []).length > 0;
  if (!hasFile) return { key: "missing", label: "文件丢失", cls: "adm-status-pill--err" };
  const { pct } = metadataCompleteness(song);
  if (pct < 70) return { key: "fix", label: "待修复", cls: "adm-status-pill--warn" };
  return { key: "ok", label: "正常", cls: "adm-status-pill--ok" };
}

function formatRoleNamesCell(names) {
  const list = names || [];
  return list.length ? escapeHtml(list.join("、")) : "—";
}

function quickFilterTagIds() {
  if (!state.quickFilterTags.length) return [];
  const byName = new Map((state.tags || []).map((t) => [t.name, t.id]));
  return state.quickFilterTags.map((n) => byName.get(n)).filter((id) => id != null);
}

function quickFilterGenreIds() {
  if (!state.quickFilterGenres.length) return [];
  const byName = new Map((state.genres || []).map((g) => [g.name, g.id]));
  return state.quickFilterGenres.map((n) => byName.get(n)).filter((id) => id != null);
}

function buildSongListQueryParams() {
  const params = new URLSearchParams();
  if (els.keywordInput && els.keywordInput.value.trim()) params.set("keyword", els.keywordInput.value.trim());
  params.set("sort_by", state.sortBy);
  params.set("sort_order", state.sortOrder);
  const offset = (state.songPage - 1) * state.songPageSize;
  params.set("offset", String(offset));
  params.set("limit", String(state.songPageSize));
  state.quickFilterLeads.forEach((v) => params.append("lead_artists", v));
  state.quickFilterLyricists.forEach((v) => params.append("lyricists", v));
  state.quickFilterComposers.forEach((v) => params.append("composers", v));
  state.quickFilterLanguages.forEach((v) => params.append("languages", v));
  state.quickFilterFormats.forEach((v) => params.append("formats", v));
  quickFilterTagIds().forEach((id) => params.append("tag_ids", String(id)));
  quickFilterGenreIds().forEach((id) => params.append("genre_ids", String(id)));
  return params;
}

function formatSongFormatLabel(song) {
  const v = (song.file_variants || [])[0];
  if (v) {
    const fmt = (v.format || "").toUpperCase();
    const br = v.bitrate ? `${v.bitrate} kbps` : "";
    return br ? `${fmt} ${br}` : fmt;
  }
  const fmts = (song.formats || []).map((f) => String(f).toUpperCase());
  return fmts.length ? fmts.join(" / ") : "—";
}

function formatStatDelta(current, previous) {
  const diff = current - (previous ?? current);
  if (diff > 0) return `较昨日 +${diff}`;
  if (diff < 0) return `较昨日 ${diff}`;
  return "";
}

function previousStatsCounts() {
  try {
    const raw = localStorage.getItem("adm-stats-last");
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function storeStatsCounts(counts) {
  try {
    localStorage.setItem("adm-stats-last", JSON.stringify(counts));
  } catch {
    /* ignore */
  }
}

function isIsoDateString(s) {
  return /^\d{4}-\d{2}-\d{2}$/.test(String(s || ""));
}

function normalizeDateInputValue(s) {
  if (s == null || s === "") return "";
  const t = String(s).trim();
  const m = t.match(/^(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})/);
  if (m) {
    const mm = m[2].padStart(2, "0");
    const dd = m[3].padStart(2, "0");
    return `${m[1]}-${mm}-${dd}`;
  }
  return t.slice(0, 10);
}

function syncReleaseDateField(releaseDate) {
  if (!els.releaseDateInput) return;
  const norm = normalizeDateInputValue(releaseDate);
  els.releaseDateInput.value = isIsoDateString(norm) ? norm : "";
}

function releaseDateFromForm() {
  const v = String(els.releaseDateInput?.value || "").trim();
  return v || null;
}

function updateSongListTotalLabel() {
  if (!els.songListTotalLabel) return;
  const n = state.songListTotal;
  const hasFilter = adminMusicHasActiveFilters();
  els.songListTotalLabel.textContent = hasFilter ? `共 ${n} 首（已筛选）` : `共 ${n} 首`;
}

function updateAdminStats() {
  const songs = state.songs || [];
  const people = state.people || [];
  const albums = new Set(songs.map((s) => (s.album || "").trim()).filter(Boolean));
  let fixCount = 0;
  let metaSum = 0;
  songs.forEach((s) => {
    const st = songAdminStatus(s);
    if (st.key === "fix" || st.key === "missing") fixCount += 1;
    metaSum += metadataCompleteness(s).pct;
  });
  const avgMeta = songs.length ? Math.round(metaSum / songs.length) : 0;
  const counts = {
    songs: state.songLibraryTotal,
    artists: people.length,
    albums: albums.size,
    fix: fixCount,
  };
  const prev = previousStatsCounts();
  storeStatsCounts(counts);
  if (els.statSongCount) els.statSongCount.textContent = String(counts.songs);
  if (els.statArtistCount) els.statArtistCount.textContent = String(counts.artists);
  if (els.statAlbumCount) els.statAlbumCount.textContent = String(counts.albums);
  if (els.statFixCount) els.statFixCount.textContent = String(counts.fix);
  if (els.statSongDelta) els.statSongDelta.textContent = formatStatDelta(counts.songs, prev.songs);
  if (els.statArtistDelta) els.statArtistDelta.textContent = formatStatDelta(counts.artists, prev.artists);
  if (els.statAlbumDelta) els.statAlbumDelta.textContent = formatStatDelta(counts.albums, prev.albums);
  if (els.statFixDelta) els.statFixDelta.textContent = formatStatDelta(counts.fix, prev.fix);
  if (els.statAiTaskPct) els.statAiTaskPct.textContent = `${avgMeta}%`;
  if (els.statAiTaskBar) els.statAiTaskBar.style.width = `${avgMeta}%`;
}

function populateAdminQuickFilterSelect(selectEl, values, selectedValues, labelFn = (v) => v) {
  if (!selectEl) return;
  const selected = new Set(Array.isArray(selectedValues) ? selectedValues : []);
  selectEl.innerHTML = values
    .map((v) => `<option value="${escSelectAttr(v)}">${escapeHtml(String(labelFn(v)))}</option>`)
    .join("");
  Array.from(selectEl.options).forEach((o) => {
    o.selected = selected.has(o.value);
  });
  if (selectEl.dataset.searchableBound === "1") refreshSearchableSelectOptions(selectEl);
  else ensureSearchableSelect(selectEl);
  syncSearchableSelectTrigger(selectEl);
}

function syncQuickFiltersFromUi() {
  state.quickFilterLeads = filterDropdownSelectedRawValues(els.filterLeadQuick);
  state.quickFilterLyricists = filterDropdownSelectedRawValues(els.filterLyricistQuick);
  state.quickFilterComposers = filterDropdownSelectedRawValues(els.filterComposerQuick);
  state.quickFilterTags = filterDropdownSelectedRawValues(els.filterTagQuick);
  state.quickFilterFormats = filterDropdownSelectedRawValues(els.filterFormatQuick);
  state.quickFilterLanguages = filterDropdownSelectedRawValues(els.filterLanguageQuick);
  state.quickFilterGenres = filterDropdownSelectedRawValues(els.filterGenreQuick);
}

function catalogPeopleNamesByType(type) {
  return peopleByType(type)
    .map((p) => p.name)
    .filter(Boolean)
    .sort((a, b) => a.localeCompare(b, "zh-CN"));
}

function populateQuickFilterOptions() {
  populateAdminQuickFilterSelect(els.filterLeadQuick, catalogPeopleNamesByType("歌手"), state.quickFilterLeads);
  populateAdminQuickFilterSelect(els.filterLyricistQuick, catalogPeopleNamesByType("作词"), state.quickFilterLyricists);
  populateAdminQuickFilterSelect(els.filterComposerQuick, catalogPeopleNamesByType("作曲"), state.quickFilterComposers);

  const tagNames = (state.tags || [])
    .map((t) => t.name)
    .filter(Boolean)
    .sort((a, b) => a.localeCompare(b, "zh-CN"));
  populateAdminQuickFilterSelect(els.filterTagQuick, tagNames, state.quickFilterTags);

  const formats = [...new Set((state.filters?.formats || []).map((f) => String(f).toLowerCase()))].filter(Boolean).sort();
  populateAdminQuickFilterSelect(els.filterFormatQuick, formats, state.quickFilterFormats, (f) => f.toUpperCase());

  const langs = (state.languages || [])
    .map((l) => l.name)
    .filter(Boolean)
    .sort((a, b) => a.localeCompare(b, "zh-CN"));
  populateAdminQuickFilterSelect(els.filterLanguageQuick, langs, state.quickFilterLanguages);

  const genreNames = (state.genres || [])
    .map((g) => g.name)
    .filter(Boolean)
    .sort((a, b) => a.localeCompare(b, "zh-CN"));
  populateAdminQuickFilterSelect(els.filterGenreQuick, genreNames, state.quickFilterGenres);
}

function initAdminMusicQuickFilters() {
  ADMIN_QUICK_FILTER_SELECTS().forEach((selectEl) => {
    selectEl.multiple = true;
    ensureSearchableSelect(selectEl);
    const wrap = selectEl.closest(".searchable-select");
    const searchInput = wrap?.querySelector(".searchable-select-search");
    const label = selectEl.dataset.filterLabel || "筛选项";
    if (searchInput) searchInput.placeholder = `搜索${label}…`;
    syncSearchableSelectTrigger(selectEl);
  });
}

function renderPagination(totalItems) {
  state.songListTotal = totalItems;
  updateSongListTotalLabel();
  const pageSize = state.songPageSize;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  if (state.songPage > totalPages) state.songPage = totalPages;
  if (els.pagePrevBtn) els.pagePrevBtn.disabled = state.songPage <= 1;
  if (els.pageNextBtn) els.pageNextBtn.disabled = state.songPage >= totalPages;
  if (!els.pageNumbers) return;
  const maxBtns = 7;
  let start = Math.max(1, state.songPage - 3);
  let end = Math.min(totalPages, start + maxBtns - 1);
  start = Math.max(1, end - maxBtns + 1);
  els.pageNumbers.innerHTML = "";
  for (let p = start; p <= end; p += 1) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = `adm-page-btn${p === state.songPage ? " is-active" : ""}`;
    b.textContent = String(p);
    b.addEventListener("click", () => {
      state.songPage = p;
      loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
    });
    els.pageNumbers.appendChild(b);
  }
}

const adminPageMusic = document.querySelector("#admin-page-music");

function openEditPanel() {
  if (els.adminEditPanel) els.adminEditPanel.classList.add("is-open");
  adminPageMusic?.classList.add("is-edit-drawer-open");
}

function closeEditPanel() {
  if (els.adminEditPanel) els.adminEditPanel.classList.remove("is-open");
  adminPageMusic?.classList.remove("is-edit-drawer-open");
}

function openCreateModal(type, editData = null) {
  state.createModalType = type;
  state.createEditData = editData;
  const titleEl = els.createModalTitle;
  const bodyEl = els.createFormBody;
  if (!bodyEl || !titleEl) return;
  bodyEl.innerHTML = "";
  const isEdit = !!editData;
  if (type === "tag") {
    titleEl.textContent = isEdit ? "编辑标签" : "新建标签";
    bodyEl.innerHTML = `<label class="form-field"><span>标签名称</span><input type="text" name="name" placeholder="输入新标签名称" value="${editData?.name || ''}" /></label>`;
  } else if (type === "language") {
    titleEl.textContent = isEdit ? "编辑语言" : "新建语言";
    bodyEl.innerHTML = `<label class="form-field"><span>语言名称</span><input type="text" name="name" placeholder="输入新语言名称" value="${editData?.name || ''}" /></label>`;
  } else if (type === "genre") {
    titleEl.textContent = isEdit ? "编辑风格" : "新建风格";
    bodyEl.innerHTML = `<label class="form-field"><span>风格名称</span><input type="text" name="name" placeholder="输入新风格名称" value="${editData?.name || ''}" /></label>`;
  } else if (type === "person") {
    titleEl.textContent = isEdit ? "编辑艺人" : "新建艺人";
    const selectedTypes = editData?.types || ["歌手"];
    bodyEl.innerHTML = `
      <label class="form-field"><span>艺人名称</span><input type="text" name="name" placeholder="输入艺人名称" value="${editData?.name || ''}" /></label>
      <div class="form-field form-field-inline"><span>类型</span>
        <label class="checkbox-inline"><input type="checkbox" name="personType" value="歌手" ${selectedTypes.includes("歌手") ? "checked" : ""} />歌手</label>
        <label class="checkbox-inline"><input type="checkbox" name="personType" value="作词" ${selectedTypes.includes("作词") ? "checked" : ""} />作词</label>
        <label class="checkbox-inline"><input type="checkbox" name="personType" value="作曲" ${selectedTypes.includes("作曲") ? "checked" : ""} />作曲</label>
      </div>
    `;
  }
  const createCard = els.createOverlay?.querySelector(".modal-card");
  if (createCard) createCard.classList.toggle("modal-card-tall", type === "person");
  els.createOverlay.classList.remove("hidden");
  setTimeout(() => bodyEl?.querySelector('input[name="name"]')?.focus(), 0);
}

function closeCreateModal() {
  state.createModalType = null;
  state.createEditData = null;
  const createCard = els.createOverlay?.querySelector(".modal-card");
  if (createCard) createCard.classList.remove("modal-card-tall");
  els.createOverlay.classList.add("hidden");
}

async function submitCreateForm(e) {
  e.preventDefault();
  const type = state.createModalType;
  const editData = state.createEditData;
  const isEdit = !!editData;
  if (!type) return;
  const bodyEl = els.createFormBody;
  const nameInput = bodyEl?.querySelector('input[name="name"]');
  const name = nameInput?.value?.trim() || "";
  if (!name) return;
  try {
    if (type === "tag") {
      if (isEdit) {
        await request(`/tags/${editData.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
        await Promise.all([loadTags(), loadFilterOptions(), loadSongs()]);
        showToast("标签已更新", "success");
      } else {
        await request("/tags", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
        await Promise.all([loadTags(), loadFilterOptions(), loadSongs()]);
        showToast("标签已创建", "success");
      }
    } else if (type === "language") {
      if (isEdit) {
        await request(`/languages/${editData.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
        await Promise.all([loadLanguages(), loadFilterOptions(), loadSongs()]);
        showToast("语言已更新", "success");
      } else {
        await request("/languages", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
        await Promise.all([loadLanguages(), loadFilterOptions(), loadSongs()]);
        showToast("语言已创建", "success");
      }
    } else if (type === "genre") {
      if (isEdit) {
        await request(`/genres/${editData.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
        await loadGenres();
        showToast("风格已更新", "success");
      } else {
        await request("/genres", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
        await loadGenres();
        showToast("风格已创建", "success");
      }
    } else if (type === "person") {
      const typeCheckboxes = bodyEl?.querySelectorAll('input[name="personType"]:checked');
      const types = typeCheckboxes && typeCheckboxes.length ? Array.from(typeCheckboxes).map(cb => cb.value) : ["歌手"];
      if (isEdit) {
        await request(`/people/${editData.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, types }) });
        await Promise.all([loadPeople(), loadSongs()]);
        showToast("艺人已更新", "success");
      } else {
        await request("/people", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, types }) });
        await Promise.all([loadPeople(), loadSongs()]);
        showToast("艺人已创建", "success");
      }
    }
    closeCreateModal();
  } catch (err) {
    showToast(isEdit ? "更新失败" : "创建失败: " + (err && err.message ? err.message : String(err)), "error");
  }
}

function openModal({ title, message, defaultValue = "", confirmText = "确定", cancelText = "取消", withInput = true }) {
  els.modalTitle.textContent = title;
  els.modalMessage.textContent = message;
  els.modalInputWrap.classList.toggle("hidden", !withInput);
  els.modalInput.value = defaultValue;
  els.modalConfirmBtn.textContent = confirmText;
  els.modalCancelBtn.textContent = cancelText;
  els.modalOverlay.classList.remove("hidden");
  if (withInput) setTimeout(() => els.modalInput.focus(), 0);
  return new Promise((resolve) => {
    modalState.resolver = resolve;
  });
}

function formatDuration(ms) {
  if (ms == null || ms === "") return "—";
  const total = Math.floor(ms / 1000);
  return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}

/** 编辑抽屉：无时长时留空，避免与 00:00 混淆 */
function formatDurationForEdit(ms) {
  if (ms == null || ms === "") return "";
  return formatDuration(ms);
}

/** 解析 mm:ss；空串 → null；非法 → { ok: false } */
function parseDurationMmSs(text) {
  const raw = String(text ?? "").trim();
  if (!raw) return { ok: true, ms: null };
  const m = /^(\d{1,3}):([0-5]\d)$/.exec(raw);
  if (!m) return { ok: false };
  const minutes = Number(m[1]);
  const seconds = Number(m[2]);
  return { ok: true, ms: minutes * 60000 + seconds * 1000 };
}

/** blur 时将 3:5 规范为 03:05 */
function normalizeDurationMmSs(text) {
  const parsed = parseDurationMmSs(text);
  if (!parsed.ok) return String(text ?? "").trim();
  if (parsed.ms == null) return "";
  return formatDuration(parsed.ms);
}

function formatSize(bytes) {
  if (!bytes) return "-";
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function escapeHtml(str) {
  const s = str == null ? "" : String(str);
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

/** 扫描/添加完成后展示跳过文件及原因 */
function showSkippedFilesModal(details) {
  const body = els.skippedFilesTableBody;
  if (!body || !els.skippedOverlay) return;
  const rows = Array.isArray(details) ? details : [];
  body.innerHTML = rows
    .map(
      (d) =>
        `<tr><td class="col-path">${escapeHtml(d.path)}</td><td>${escapeHtml(d.reason || "未知原因")}</td></tr>`
    )
    .join("");
  els.skippedOverlay.classList.remove("hidden");
}

function closeSkippedFilesModal() {
  els.skippedOverlay?.classList.add("hidden");
}

/** 抽屉内音频行：图标按钮（title 为悬停说明） */
const VARIANT_ICONS = {
  play: `<svg class="icon-btn-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>`,
  download: `<svg class="icon-btn-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>`,
  rename: `<svg class="icon-btn-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a.996.996 0 0 0 0-1.41l-2.34-2.34a.996.996 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>`,
  delete: `<svg class="icon-btn-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`,
};

/** 从展示用文件名得到主文件名（去掉与 format 一致的后缀） */
function filenameStemForRename(displayName, format) {
  const fmt = (format || "").toLowerCase().replace(/^\./, "");
  if (!fmt || !displayName) return (displayName || "").trim();
  const re = new RegExp(`\\.${fmt.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`, "i");
  return displayName.replace(re, "").trim();
}

async function parseResponseError(res) {
  const text = await res.text();
  try {
    const j = JSON.parse(text);
    if (j.detail !== undefined) {
      return typeof j.detail === "string" ? j.detail : Array.isArray(j.detail) ? j.detail.map((x) => x.msg || JSON.stringify(x)).join("; ") : JSON.stringify(j.detail);
    }
  } catch (_) {
    /* ignore */
  }
  return text || `HTTP ${res.status}`;
}

function normalizeDownloadFmt(f) {
  return String(f || "").toLowerCase().replace(/^\./, "").trim();
}

/** 与后端 is_playable_web 语义对齐（不含 APE）；用于列表试听/格式下拉 */
const WEB_PLAYABLE_AUDIO_FORMATS = new Set(["mp3", "m4a", "aac", "ogg", "wav", "flac"]);
const MSG_NO_WEB_PLAY_PREVIEW = "暂无可浏览器播放的音频";

function songHasWebPlayableAudio(song) {
  if (!song) return false;
  const variants = song.file_variants || [];
  const fromV = variants.map((v) => normalizeDownloadFmt(v.format)).filter(Boolean);
  if (fromV.length) return fromV.some((f) => WEB_PLAYABLE_AUDIO_FORMATS.has(f));
  const fm = (song.formats || []).map((x) => normalizeDownloadFmt(x)).filter(Boolean);
  if (fm.length) return fm.some((f) => WEB_PLAYABLE_AUDIO_FORMATS.has(f));
  if (song.file_format) return WEB_PLAYABLE_AUDIO_FORMATS.has(normalizeDownloadFmt(song.file_format));
  return false;
}

function webPlayableFileVariants(variants) {
  if (!variants || !variants.length) return [];
  return variants.filter((v) => WEB_PLAYABLE_AUDIO_FORMATS.has(normalizeDownloadFmt(v.format)));
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
  return `/songs/${songId}/download${q ? `?${q}` : ""}`;
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

async function execBatchDownload(songIds, formats) {
  const res = await fetch("/admin/songs/batch-download", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "*/*" },
    body: JSON.stringify({ song_ids: songIds, formats }),
  });
  if (!res.ok) {
    const msg = await parseResponseError(res);
    throw new Error(msg);
  }
  const disp = res.headers.get("Content-Disposition") || "";
  let filename = "music_download.zip";
  const mStar = /filename\*=UTF-8''([^;\s]+)/i.exec(disp);
  const mPlain = /filename="([^"]+)"/i.exec(disp);
  if (mStar) {
    try {
      filename = decodeURIComponent(mStar[1].trim());
    } catch (_) {
      filename = mStar[1].trim();
    }
  } else if (mPlain) {
    filename = mPlain[1];
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
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
    const single = songs.length === 1 ? songs[0] : null;
    hint.textContent = single
      ? `「${single.title || "歌曲"}」：勾选要下载的格式（多选将打包为 ZIP）`
      : `已选 ${songs.length} 首：下载各首中存在的勾选格式；总文件数大于 1 时打包为 ZIP。`;

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

/** 单曲 / 批量：先解析可用格式；多种格式时弹窗多选；单文件直链下载，多文件服务端 ZIP */
async function startDownloadFlow(songs) {
  if (!songs?.length) return;
  try {
    const list = await Promise.all(songs.map(ensureSongFormatSource));
    const union = unionFormatsFromSongs(list);
    if (!union.length) {
      showToast("没有可下载的音频格式", "error");
      return;
    }

    const run = async (selectedFormats) => {
      if (list.length === 1) {
        window.location.href = songDownloadUrl(list[0].id, selectedFormats);
      } else {
        await execBatchDownload(
          list.map((s) => s.id),
          selectedFormats
        );
      }
      showToast("正在下载…", "success");
    };

    if (union.length === 1) {
      await run([union[0]]);
      return;
    }

    const selected = await openDownloadFormatsPicker(list, union);
    if (!selected?.length) return;
    await run(selected);
  } catch (err) {
    showToast(`下载失败: ${err.message || err}`, "error");
  }
}

function setupVariantListFileActions() {
  if (!els.variantList || state.variantFileActionsSetup) return;
  state.variantFileActionsSetup = true;
  els.variantList.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-variant-file-action]");
    if (!btn) return;
    e.preventDefault();
    const fileId = Number(btn.dataset.fileId);
    const action = btn.dataset.variantFileAction;
    if (!fileId) return;
    const item = btn.closest(".variant-item");
    const titleEl = item?.querySelector(".variant-file-title");
    const titleText = titleEl ? titleEl.textContent.trim() : "音频";

    if (action === "preview") {
      if (els.adminAudioPlayer) {
        els.adminAudioPlayer.src = resolveMediaSrc(`/song-files/${fileId}/stream`);
        els.adminAudioPlayer.play().catch(() => showToast("无法播放", "error"));
        updateAdminPlayPauseIcon();
      }
      const previewSong = state.editingSongId
        ? state.songs.find((s) => adminSongIdEquals(s.id, state.editingSongId)) || { title: titleText }
        : { title: titleText };
      const fmt = (btn.dataset.format || "").toUpperCase();
      updateAdminPlayerShell(previewSong, fmt ? { selected_format: fmt } : null);
      return;
    }
    if (action === "download") {
      const link = document.createElement("a");
      link.href = `/song-files/${fileId}/download`;
      link.download = "";
      document.body.appendChild(link);
      link.click();
      link.remove();
      return;
    }
    if (action === "rename") {
      const fileFormat = (btn.dataset.fileFormat || "").trim().toLowerCase().replace(/^\./, "");
      if (!fileFormat) {
        showToast("无法重命名：缺少格式信息", "error");
        return;
      }
      const defaultStem = filenameStemForRename(titleText, fileFormat);
      const val = await openModal({
        title: "重命名音频文件",
        message: `仅可修改主文件名（不含扩展名），格式固定为 .${fileFormat}，不可更改。`,
        defaultValue: defaultStem,
        confirmText: "保存",
        withInput: true,
      });
      if (val == null) return;
      let stem = String(val).trim();
      if (stem.toLowerCase().endsWith(`.${fileFormat}`)) {
        stem = stem.slice(0, -(fileFormat.length + 1)).trim();
      }
      if (!stem) {
        showToast("主文件名不能为空", "error");
        return;
      }
      if (/[/\\]/.test(stem)) {
        showToast("名称不能包含路径分隔符", "error");
        return;
      }
      const name = `${stem}.${fileFormat}`;
      try {
        await request(`/song-files/${fileId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ original_filename: name }),
        });
        showToast("已更新文件名", "success");
        if (state.editingSongId) {
          await openEditModal(state.editingSongId, state.editingCurrentFileId, { preserveMetadata: true });
        }
        await loadSongs().catch(() => {});
      } catch (err) {
        showToast(`重命名失败: ${err.message || err}`, "error");
      }
      return;
    }
    if (action === "delete") {
      const ok = await openModal({
        title: "删除音频文件",
        message: `确定删除「${titleText}」吗？将从曲库与存储中移除该文件，且不可恢复。`,
        confirmText: "删除",
        withInput: false,
      });
      if (!ok) return;
      try {
        await request(`/song-files/${fileId}`, { method: "DELETE" });
        showToast("音频文件已删除", "success");
        if (state.editingSongId) {
          await openEditModal(state.editingSongId, state.editingCurrentFileId, { preserveMetadata: true });
        }
        await loadSongs().catch(() => {});
      } catch (err) {
        showToast(`删除失败: ${err.message || err}`, "error");
      }
    }
  });
}

function formatDate(value) {
  if (!value) return "-";
  const isoValue = /z$/i.test(value) || /[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`;
  const formatter = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
  const parts = Object.fromEntries(formatter.formatToParts(new Date(isoValue)).map((part) => [part.type, part.value]));
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
}

function escSelectAttr(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;");
}

function escapeHtmlUserText(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function initAdminFilterMultiSelectDefault(selectEl) {
  if (!selectEl?.multiple) return;
  Array.from(selectEl.options).forEach((o) => {
    o.selected = false;
  });
}

function renderSelectOptions(selectEl, values, formatter = (x) => x) {
  selectEl.innerHTML = values.map((value) => `<option value="${escSelectAttr(value)}">${escapeHtmlUserText(String(formatter(value)))}</option>`).join("");
  initAdminFilterMultiSelectDefault(selectEl);
  ensureSearchableSelect(selectEl);
  refreshSearchableSelectOptions(selectEl);
}

function formatsFromDetailFiles(files) {
  const seen = new Set();
  const out = [];
  for (const f of files || []) {
    const raw = String(f.format || "")
      .trim()
      .toLowerCase()
      .replace(/^\./, "");
    if (!raw || seen.has(raw)) continue;
    seen.add(raw);
    out.push(raw.toUpperCase());
  }
  return out;
}

function renderEditFormatsReadonly(files) {
  if (!els.editFormatsReadonly) return;
  const fmts = formatsFromDetailFiles(files);
  els.editFormatsReadonly.innerHTML = fmts.length
    ? fmts.map((f) => `<span class="adm-tag-chip adm-format-chip">${escapeHtmlUserText(f)}</span>`).join("")
    : '<span class="muted">—</span>';
}

function peopleByType(type) {
  return state.people.filter((person) => (person.types || []).includes(type));
}

const ARTIST_RECENT_STORAGE_KEY = "pm_admin_artist_recent_v1";

function artistRoleKeyFromType(type) {
  if (type === "作词") return "lyricist";
  if (type === "作曲") return "composer";
  return "lead";
}

function loadArtistRecentMaps() {
  try {
    const raw = localStorage.getItem(ARTIST_RECENT_STORAGE_KEY);
    if (!raw) return { lead: {}, lyricist: {}, composer: {} };
    const o = JSON.parse(raw);
    return {
      lead: o.lead && typeof o.lead === "object" ? o.lead : {},
      lyricist: o.lyricist && typeof o.lyricist === "object" ? o.lyricist : {},
      composer: o.composer && typeof o.composer === "object" ? o.composer : {},
    };
  } catch {
    return { lead: {}, lyricist: {}, composer: {} };
  }
}

function saveArtistRecentMaps(maps) {
  try {
    localStorage.setItem(ARTIST_RECENT_STORAGE_KEY, JSON.stringify(maps));
  } catch {
    /* ignore quota */
  }
}

function touchArtistRecent(roleKey, artistId) {
  const id = Number(artistId);
  if (!id) return;
  const maps = loadArtistRecentMaps();
  if (!maps[roleKey]) maps[roleKey] = {};
  maps[roleKey][String(id)] = Date.now();
  saveArtistRecentMaps(maps);
}

function recordMetadataArtistRecent(leadIds, lyricistIds, composerIds) {
  (leadIds || []).forEach((x) => touchArtistRecent("lead", x));
  (lyricistIds || []).forEach((x) => touchArtistRecent("lyricist", x));
  (composerIds || []).forEach((x) => touchArtistRecent("composer", x));
}

const LANGUAGE_RECENT_KEY = "pm_admin_language_recent_v1";
const TAG_RECENT_KEY = "pm_admin_tag_recent_v1";
const GENRE_RECENT_KEY = "pm_admin_genre_recent_v1";

function loadIdRecentMap(key) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return {};
    const o = JSON.parse(raw);
    return o && typeof o === "object" ? o : {};
  } catch {
    return {};
  }
}

function saveIdRecentMap(key, map) {
  try {
    localStorage.setItem(key, JSON.stringify(map));
  } catch {
    /* quota */
  }
}

function touchIdRecent(key, entityId) {
  const id = Number(entityId);
  if (!id) return;
  const m = loadIdRecentMap(key);
  m[String(id)] = Date.now();
  saveIdRecentMap(key, m);
}

function sortByRecentName(items, recentKey) {
  const m = loadIdRecentMap(recentKey);
  return [...items].sort((a, b) => {
    const ta = m[String(a.id)] || 0;
    const tb = m[String(b.id)] || 0;
    if (tb !== ta) return tb - ta;
    return (a.name || "").localeCompare(b.name || "", "zh-CN");
  });
}

function touchLanguageRecent(id) {
  touchIdRecent(LANGUAGE_RECENT_KEY, id);
}

function touchTagRecent(id) {
  touchIdRecent(TAG_RECENT_KEY, id);
}

function touchGenreRecent(id) {
  touchIdRecent(GENRE_RECENT_KEY, id);
}

function recordMetadataLanguageGenreRecent(languageIds, genreIds) {
  (languageIds || []).forEach((x) => touchLanguageRecent(x));
  (genreIds || []).forEach((x) => touchGenreRecent(x));
}

function sortPeopleByRoleRecent(people, roleKey) {
  const maps = loadArtistRecentMaps();
  const m = maps[roleKey] || {};
  return [...people].sort((a, b) => {
    const ta = m[String(a.id)] || 0;
    const tb = m[String(b.id)] || 0;
    if (tb !== ta) return tb - ta;
    return (a.name || "").localeCompare(b.name || "", "zh-CN");
  });
}

function buildCandidatePeopleForField(type, selectedIdSet) {
  const byType = peopleByType(type);
  const extra = (state.people || []).filter(
    (p) => selectedIdSet.has(p.id) && !byType.some((x) => x.id === p.id),
  );
  const seen = new Set();
  const out = [];
  for (const p of [...extra, ...byType]) {
    if (seen.has(p.id)) continue;
    seen.add(p.id);
    out.push(p);
  }
  const roleKey = artistRoleKeyFromType(type);
  return sortPeopleByRoleRecent(out, roleKey);
}

/** 点击选项行（除复选框外）切换勾选；搜索框点击不处理 */
function attachMultiSelectOptionRowClick(menu) {
  menu.addEventListener("click", (e) => {
    const search = menu.querySelector(".multi-select-search");
    if (search && (e.target === search || search.contains(e.target))) {
      e.stopPropagation();
      return;
    }
    const row = e.target.closest(".artist-option");
    if (row && menu.contains(row) && !(e.target instanceof HTMLInputElement && e.target.type === "checkbox")) {
      const cb = row.querySelector('input[type="checkbox"]');
      if (cb) {
        e.preventDefault();
        cb.checked = !cb.checked;
        cb.dispatchEvent(new Event("change", { bubbles: true }));
      }
    }
    e.stopPropagation();
  });
}

function renderArtistMultiSelect(container, selectedIds = [], type = "歌手") {
  const roleKey = artistRoleKeyFromType(type);
  const validSelectedIds = selectedIds.filter((id) => (state.people || []).some((person) => person.id === id));
  container._searchText = "";
  container._artistSelectedIds = new Set(validSelectedIds);
  container._artistFieldType = type;
  container._artistFieldRoleKey = roleKey;

  container.innerHTML = `
    <div class="multi-select-trigger" role="button" tabindex="0">请选择</div>
    <div class="multi-select-menu hidden">
      <input type="text" class="multi-select-search" placeholder="搜索、筛选或输入新艺人…" autocomplete="off" />
      <div class="multi-select-options"></div>
    </div>
  `;
  const trigger = container.querySelector(".multi-select-trigger");
  const menu = container.querySelector(".multi-select-menu");
  const searchInput = menu.querySelector(".multi-select-search");
  const optionsEl = menu.querySelector(".multi-select-options");

  const updateTrigger = () => {
    const names = Array.from(container._artistSelectedIds)
      .map((id) => (state.people || []).find((p) => p.id === id)?.name)
      .filter(Boolean);
    trigger.innerHTML = names.length
      ? `<span class="tag-list">${names.map((n) => `<span class="tag">${escapeHtmlUserText(n)}</span>`).join("")}</span>`
      : "请选择";
  };

  const metaRowsForKeyword = (kwRaw) => {
    const kw = kwRaw.trim();
    if (!kw) return { html: "" };
    const lower = kw.toLowerCase();
    const exact = (state.people || []).find((p) => (p.name || "").trim().toLowerCase() === lower);
    if (exact && !(exact.types || []).includes(type)) {
      return {
        html: `<div class="multi-select-meta-hint">已有同名艺人，可补全类型：</div>
          <div class="multi-select-meta-row" tabindex="0" role="button" data-action="addtype" data-person-id="${exact.id}">
            将「${escapeHtmlUserText(kw)}」添加为「${escapeHtmlUserText(type)}」
          </div>`,
      };
    }
    if (!exact) {
      return {
        html: `<div class="multi-select-meta-hint">无完全匹配时可新建：</div>
          <div class="multi-select-meta-row" tabindex="0" role="button" data-action="create">
            创建并添加「${escapeHtmlUserText(kw)}」
          </div>`,
      };
    }
    return { html: "" };
  };

  const rebuildOptions = () => {
    const kw = (container._searchText || "").trim();
    const sel = container._artistSelectedIds;
    const candidates = buildCandidatePeopleForField(type, sel);
    const list = !kw ? candidates : candidates.filter((p) => fuzzyMatchName(p.name, kw) || sel.has(p.id));
    const meta = metaRowsForKeyword(container._searchText || "");

    let body = meta.html;
    if (list.length) {
      body += list
        .map(
          (person) =>
            `<div class="artist-option"><input type="checkbox" value="${person.id}" ${sel.has(person.id) ? "checked" : ""} /><span>${escapeHtmlUserText(person.name)}</span></div>`,
        )
        .join("");
    }
    if (!list.length && !meta.html) {
      body += '<div class="multi-select-empty muted" style="padding:10px 8px;font-size:13px;">无匹配结果</div>';
    }
    optionsEl.innerHTML = body;
  };

  const setMetaBusy = (busy) => {
    menu.querySelectorAll(".multi-select-meta-row").forEach((el) => el.classList.toggle("is-busy", busy));
  };

  menu.addEventListener("click", async (e) => {
    const addRow = e.target.closest('.multi-select-meta-row[data-action="addtype"]');
    const createRow = e.target.closest('.multi-select-meta-row[data-action="create"]');
    if (!addRow && !createRow) return;
    e.preventDefault();
    e.stopPropagation();
    const kw = (container._searchText || "").trim();
    if (!kw) return;
    try {
      setMetaBusy(true);
      if (addRow) {
        const pid = Number(addRow.dataset.personId);
        const person = (state.people || []).find((p) => p.id === pid);
        if (!person) throw new Error("找不到该艺人");
        const types = new Set(person.types || []);
        types.add(type);
        const updated = await request(`/people/${person.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: person.name, types: [...types] }),
        });
        const idx = (state.people || []).findIndex((p) => p.id === updated.id);
        if (idx >= 0) state.people[idx] = updated;
        else state.people.push(updated);
        touchArtistRecent(roleKey, updated.id);
        container._artistSelectedIds.add(updated.id);
        await loadFilterOptions();
        populateQuickFilterOptions();
      } else {
        const created = await request("/people", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: kw, types: [type] }),
        });
        if (!state.people) state.people = [];
        state.people.push(created);
        state.people.sort((a, b) => (a.name || "").localeCompare(b.name || "", "zh-CN"));
        touchArtistRecent(roleKey, created.id);
        container._artistSelectedIds.add(created.id);
        container._searchText = "";
        if (searchInput) searchInput.value = "";
        await loadFilterOptions();
        populateQuickFilterOptions();
      }
      updateTrigger();
      rebuildOptions();
      showToast("已添加艺人", "success");
    } catch (err) {
      showToast(err.message || String(err), "error");
    } finally {
      setMetaBusy(false);
    }
  });

  updateTrigger();
  rebuildOptions();

  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (activeMultiSelect && activeMultiSelect !== menu) activeMultiSelect.classList.add("hidden");
    const willOpen = menu.classList.contains("hidden");
    menu.classList.toggle("hidden", !willOpen);
    activeMultiSelect = willOpen ? menu : null;
    if (willOpen) setTimeout(() => searchInput?.focus(), 0);
  });
  searchInput?.addEventListener("click", (ev) => ev.stopPropagation());
  searchInput?.addEventListener("keydown", (ev) => {
    if (ev.key !== "Enter") return;
    ev.preventDefault();
    ev.stopPropagation();
    const addTypeEl = menu.querySelector('.multi-select-meta-row[data-action="addtype"]');
    const createEl = menu.querySelector('.multi-select-meta-row[data-action="create"]');
    if (addTypeEl) addTypeEl.click();
    else if (createEl) createEl.click();
  });
  searchInput?.addEventListener("input", (event) => {
    container._searchText = event.target.value;
    rebuildOptions();
  });
  attachMultiSelectOptionRowClick(menu);
  menu.addEventListener("change", (event) => {
    if (event.target.type === "checkbox") {
      const id = Number(event.target.value);
      if (event.target.checked) {
        container._artistSelectedIds.add(id);
        touchArtistRecent(roleKey, id);
      } else container._artistSelectedIds.delete(id);
      updateTrigger();
    }
  });
}

function getSelectedArtistIds(container) {
  if (container._artistSelectedIds instanceof Set) return Array.from(container._artistSelectedIds);
  return Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map((node) => Number(node.value));
}

function positionTypeMenuInEditForm(container) {
  const inlineEdit = container.closest('.inline-edit-types');
  if (!inlineEdit) return;
  const trigger = container.querySelector('.multi-select-trigger');
  const menu = container.querySelector('.multi-select-menu');
  if (!trigger || !menu) return;
  const rect = trigger.getBoundingClientRect();
  menu.style.position = 'fixed';
  menu.style.top = (rect.bottom + 6) + 'px';
  menu.style.left = rect.left + 'px';
  menu.style.width = Math.max(rect.width, 200) + 'px';
  menu.style.right = 'auto';
}

function renderTypeMultiSelect(container, selectedTypes = ["歌手"]) {
  const options = ["歌手", "作词", "作曲"];
  const isInEditForm = !!container.closest('.inline-edit-types');
  container.innerHTML = `
    <div class="multi-select-trigger" role="button" tabindex="0">${selectedTypes.length ? `<span class="tag-list">${selectedTypes.map((name) => `<span class="tag">${name}</span>`).join("")}</span>` : "请选择类型"}</div>
    <div class="multi-select-menu hidden${isInEditForm ? ' multi-select-menu-inline-edit' : ''}">
      <div class="multi-select-options">
        ${options.map((type) => `<label class="multi-select-option"><input type="checkbox" value="${type}" ${selectedTypes.includes(type) ? "checked" : ""} /><span>${type}</span></label>`).join("")}
      </div>
    </div>
  `;
  const trigger = container.querySelector('.multi-select-trigger');
  const menu = container.querySelector('.multi-select-menu');
  trigger.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (activeMultiSelect && activeMultiSelect !== menu) {
      activeMultiSelect.classList.add('hidden');
    }
    const willOpen = menu.classList.contains('hidden');
    if (willOpen) {
      container.dataset.initialTypes = JSON.stringify(getSelectedTypes(container));
      if (isInEditForm) positionTypeMenuInEditForm(container);
    }
    menu.classList.toggle('hidden', !willOpen);
    activeMultiSelect = willOpen ? menu : null;
  });
  menu.addEventListener('click', (event) => {
    event.stopPropagation();
  });
  menu.addEventListener('change', (event) => {
    if (event.target.type === 'checkbox') {
      renderTypeMultiSelect(container, getSelectedTypes(container));
      const nextMenu = container.querySelector('.multi-select-menu');
      nextMenu?.classList.remove('hidden');
      activeMultiSelect = nextMenu || null;
      if (container.closest('.inline-edit-types')) positionTypeMenuInEditForm(container);
    }
  });
}

function getSelectedTypes(container) {
  return Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map((node) => node.value);
}


function renderSortIndicators() {
  els.sortButtons.forEach((button) => {
    const baseLabel = button.dataset.label || button.textContent.replace(/[ ↑↓]/g, "");
    button.dataset.label = baseLabel;
    const arrow = button.dataset.sort === state.sortBy ? (state.sortOrder === "asc" ? " ↑" : " ↓") : "";
    button.textContent = `${baseLabel}${arrow}`;
  });
}

function renderSongs() {
  if (!els.songTableBody) return;
  els.songTableBody.innerHTML = "";
  const pageSongs = state.songs || [];
  const listTotal = state.songListTotal;
  if (!pageSongs.length) {
    els.songTableBody.innerHTML = '<tr><td colspan="17" class="empty-cell">暂无歌曲</td></tr>';
    renderSortIndicators();
    renderPagination(listTotal);
    updateAdminStats();
    return;
  }

  const allSelected = pageSongs.length > 0 && pageSongs.every((s) => state.selectedSongs.has(s.id));
  if (els.selectAllSongs) els.selectAllSongs.checked = allSelected;

  pageSongs.forEach((song, index) => {
    const tr = document.createElement("tr");
    tr.dataset.songId = String(song.id);
    const isPlaying = state.playingSongId != null && adminSongIdEquals(state.playingSongId, song.id);
    const isEditSelected = state.activeSongId != null && adminSongIdEquals(state.activeSongId, song.id);
    if (isPlaying) tr.classList.add("is-playing");
    else if (isEditSelected) tr.classList.add("is-active");
    const isChecked = state.selectedSongs.has(song.id);
    const canWebPreview = songHasWebPlayableAudio(song);
    const { pct } = metadataCompleteness(song);
    const tagsText = (song.tags || []).length ? escapeHtml(song.tags.join("、")) : "—";
    const playMenuItem = canWebPreview
      ? '<button class="btn menu-btn" data-role="play" type="button">▶ 试听</button>'
      : `<button class="btn menu-btn" data-role="play" type="button" disabled title="${escapeHtml(MSG_NO_WEB_PLAY_PREVIEW)}">▶ 试听</button>`;
    tr.innerHTML = `
      <td class="col-check" data-stop-row="1"><input type="checkbox" class="song-checkbox" value="${song.id}" ${isChecked ? "checked" : ""} /></td>
      <td class="col-title"><strong>${escapeHtml(song.title || "—")}</strong></td>
      <td>${escapeHtml(song.lead_artist || "—")}</td>
      <td>${formatRoleNamesCell(song.lyricists)}</td>
      <td>${formatRoleNamesCell(song.composers)}</td>
      <td>${escapeHtml(song.album || "—")}</td>
      <td>${escapeHtml(song.language || "—")}</td>
      <td>${escapeHtml(song.genre || "—")}</td>
      <td>${escapeHtml(song.film_tv || "—")}</td>
      <td>${tagsText}</td>
      <td>${escapeHtml(formatSongFormatLabel(song))}</td>
      <td>${formatDuration(song.duration_ms)}</td>
      <td>${escapeHtml(song.release_date || "—")}</td>
      <td>
        <div class="adm-meta-bar">
          <div class="adm-meta-progress"><i style="width:${pct}%"></i></div>
          <span class="adm-meta-pct">${pct}%</span>
        </div>
      </td>
      <td>${formatDate(song.created_at)}</td>
      <td>${formatDate(song.updated_at)}</td>
      <td class="col-actions" data-stop-row="1">
        <div class="adm-actions-inner">
          <div class="table-more">
            <button class="adm-icon-btn table-more-btn" data-role="more" type="button" aria-label="更多">⋮</button>
            <div class="table-more-menu hidden" data-role="menu">
              <button class="btn menu-btn" data-role="edit" type="button">✎ 编辑</button>
              ${playMenuItem}
              <button class="btn menu-btn" data-role="download" type="button">↓ 下载</button>
              <button class="btn menu-btn danger-text" data-role="delete" type="button">🗑 删除</button>
            </div>
          </div>
        </div>
      </td>
    `;
    const checkbox = tr.querySelector('.song-checkbox');
    checkbox.addEventListener('change', (e) => {
      e.stopPropagation();
      if (checkbox.checked) {
        state.selectedSongs.add(song.id);
      } else {
        state.selectedSongs.delete(song.id);
      }
      updateBatchButtons();
    });
    tr.addEventListener("click", (e) => {
      if (e.target.closest("[data-stop-row]")) return;
      state.activeSongId = song.id;
      document.querySelectorAll(".adm-songs-table tbody tr.is-active").forEach((r) => r.classList.remove("is-active"));
      const nowPlaying = state.playingSongId != null && adminSongIdEquals(state.playingSongId, song.id);
      if (!nowPlaying) tr.classList.add("is-active");
      openEditModal(song.id).catch((err) => showToast(`打开编辑失败: ${err.message || err}`, "error"));
    });
    const moreBtn = tr.querySelector('[data-role="more"]');
    const menu = tr.querySelector('[data-role="menu"]');
    const tableMore = moreBtn.closest(".table-more");
    moreBtn.addEventListener("click", (ev) => {
      ev.stopPropagation();
      document.querySelectorAll('.table-more-menu').forEach((node) => {
        if (node !== menu) {
          node.classList.add("hidden");
          node.classList.remove("table-more-menu-fixed");
          node.style.top = "";
          node.style.left = "";
          node.style.right = "";
          const home = node._tableMoreHome;
          if (home && node.parentNode === document.body) home.appendChild(node);
        }
      });
      const wasHidden = menu.classList.contains("hidden");
      menu.classList.toggle("hidden");
      if (wasHidden) {
        menu._tableMoreHome = tableMore;
        document.body.appendChild(menu);
        menu.classList.add("table-more-menu-fixed");
        const rect = moreBtn.getBoundingClientRect();
        const gap = 2;
        menu.style.top = `${rect.bottom + gap}px`;
        menu.style.left = `${rect.right - 110}px`;
        menu.style.right = "auto";
      } else {
        menu.classList.remove("table-more-menu-fixed");
        menu.style.top = "";
        menu.style.left = "";
        menu.style.right = "";
        if (tableMore) tableMore.appendChild(menu);
      }
    });
    function closeMenuAndReturnHome() {
      menu.classList.add("hidden");
      menu.classList.remove("table-more-menu-fixed");
      menu.style.top = "";
      menu.style.left = "";
      menu.style.right = "";
      if (tableMore) tableMore.appendChild(menu);
    }
    tr.querySelector('[data-role="play"]')?.addEventListener("click", (ev) => {
      ev.stopPropagation();
      closeMenuAndReturnHome();
      if (!canWebPreview) return;
      const fmt = state.songFormatPreference[song.id] || "";
      playSongInAdmin(song.id, fmt, index).catch((err) => showToast(`播放失败: ${err.message || err}`, "error"));
    });
    tr.querySelector('[data-role="download"]')?.addEventListener("click", async (ev) => {
      ev.stopPropagation();
      closeMenuAndReturnHome();
      await startDownloadFlow([song]);
    });
    const openRowEdit = (ev) => {
      ev.stopPropagation();
      closeMenuAndReturnHome();
      state.activeSongId = song.id;
      document.querySelectorAll(".adm-songs-table tbody tr.is-active").forEach((r) => r.classList.remove("is-active"));
      if (state.playingSongId == null || !adminSongIdEquals(state.playingSongId, song.id)) tr.classList.add("is-active");
      openEditModal(song.id).catch((err) => showToast(`打开编辑失败: ${err.message || err}`, "error"));
    };
    tr.querySelector('[data-role="edit"]')?.addEventListener("click", openRowEdit);
    tr.querySelector('[data-role="delete"]').addEventListener("click", async (ev) => {
      ev.stopPropagation();
      closeMenuAndReturnHome();
      const ok = await openModal({ title: "删除歌曲", message: `确认删除歌曲「${song.title}」吗？`, confirmText: "删除", withInput: false });
      if (!ok) return;
      await request(`/songs/${song.id}`, { method: "DELETE" });
      await Promise.all([loadSongs(), loadFilterOptions()]);
      showToast("歌曲已删除", "success");
    });
    els.songTableBody.appendChild(tr);
  });

  renderSortIndicators();
  updateBatchButtons();
  renderPagination(listTotal);
  updateAdminStats();
}

function updateBatchButtons() {
  const selectedCount = state.selectedSongs.size;
  if (selectedCount > 0) {
    els.batchDeleteBtn?.classList.remove("hidden");
    if (els.batchDeleteBtn) els.batchDeleteBtn.textContent = `批量删除 (${selectedCount})`;
    els.batchDownloadBtn?.classList.remove("hidden");
    if (els.batchDownloadBtn) els.batchDownloadBtn.textContent = `批量下载 (${selectedCount})`;
    els.relocateSelectedStorageBtn?.classList.remove("hidden");
    if (els.relocateSelectedStorageBtn) els.relocateSelectedStorageBtn.textContent = `同步存储路径 (${selectedCount})`;
  } else {
    els.batchDeleteBtn?.classList.add("hidden");
    els.batchDownloadBtn?.classList.add("hidden");
    els.relocateSelectedStorageBtn?.classList.add("hidden");
  }
  if (selectedCount >= 2) {
    els.batchMergeSelectedBtn?.classList.remove("hidden");
    if (els.batchMergeSelectedBtn) els.batchMergeSelectedBtn.textContent = `合并所选歌曲 (${selectedCount})`;
  } else {
    els.batchMergeSelectedBtn?.classList.add("hidden");
  }
}

function getSelectedSongIds() {
  return Array.from(state.selectedSongs);
}

async function batchDeleteSongs() {
  const ids = getSelectedSongIds();
  if (!ids.length) return;
  const ok = await openModal({ title: "批量删除", message: `确认删除选中的 ${ids.length} 首歌曲吗？`, confirmText: "删除", withInput: false });
  if (!ok) return;
  for (const id of ids) {
    await request(`/songs/${id}`, { method: "DELETE" });
  }
  state.selectedSongs.clear();
  await Promise.all([loadSongs(), loadFilterOptions()]);
  showToast("批量删除完成", "success");
}

async function batchMergeDuplicateSongs() {
  const ok = await openModal({
    title: "合并重复曲目",
    message:
      "将按「相同标题 + 相同主艺人 + 相近时长」自动合并重复歌曲，保留 id 最小的为主曲。是否继续？",
    confirmText: "合并",
    withInput: false,
  });
  if (!ok) return;
  try {
    const stats = await request("/admin/merge-duplicate-songs", { method: "POST" });
    const g = stats.merged_duplicate_groups ?? 0;
    const s = stats.merged_slave_songs ?? 0;
    showToast(g || s ? `已处理 ${g} 组重复，合并 ${s} 条从曲（仅元数据与文件归属，未删音频）` : "未发现可合并的重复曲目", g || s ? "success" : "info");
    await Promise.all([loadSongs(), loadFilterOptions()]);
  } catch (err) {
    showToast(`合并失败: ${err.message || err}`, "error");
  }
}

async function relocateSelectedSongStorage() {
  const ids = [...getSelectedSongIds()].sort((a, b) => a - b);
  if (!ids.length) {
    showToast("请先勾选至少一首歌曲", "error");
    return;
  }
  const ok = await openModal({
    title: "按元数据同步存储路径",
    message: `将对勾选的 ${ids.length} 首歌曲，按当前「原唱、歌名、文件名」规则逐首调整对象存储路径（桶内复制成功后删除旧键）。确定执行？`,
    withInput: false,
    confirmText: "开始同步",
  });
  if (!ok) return;

  const toggleBarriers = [els.relocateSelectedStorageBtn, els.batchMergeSelectedBtn, els.batchDeleteBtn, els.batchDownloadBtn];
  const setBusy = (busy) => {
    toggleBarriers.forEach((el) => {
      if (el) el.disabled = busy;
    });
  };

  els.relocateProgressWrap.classList.remove("hidden");
  els.relocateProgressText.textContent = "正在同步存储路径...";
  els.relocateProgressFill.style.width = "0%";
  setBusy(true);

  let filesMoved = 0;
  const errors = [];
  try {
    for (let i = 0; i < ids.length; i++) {
      const id = ids[i];
      els.relocateProgressStats.textContent = `处理中 ${i + 1} / ${ids.length} · 歌曲 ID ${id}`;
      els.relocateProgressFill.style.width = `${Math.round((i / Math.max(ids.length, 1)) * 100)}%`;
      try {
        const res = await request(`/admin/songs/${id}/relocate-storage`, { method: "POST" });
        filesMoved += res.files_moved ?? 0;
      } catch (err) {
        errors.push({ id, message: err.message || String(err) });
      }
      els.relocateProgressFill.style.width = `${Math.round(((i + 1) / ids.length) * 100)}%`;
    }
    els.relocateProgressText.textContent = "同步完成";
    els.relocateProgressStats.textContent = errors.length
      ? `完成 ${ids.length} 首，${errors.length} 首失败`
      : `完成 ${ids.length} 首`;
    const base = `已处理 ${ids.length} 首，共搬迁 ${filesMoved} 个文件`;
    showToast(errors.length ? `${base}；${errors.length} 首失败` : base, errors.length ? "error" : "success");
    await loadSongs().catch(() => {});
  } catch (err) {
    showToast(`同步失败: ${err.message || err}`, "error");
  } finally {
    setBusy(false);
    setTimeout(() => {
      els.relocateProgressWrap.classList.add("hidden");
    }, errors.length ? 2200 : 900);
  }
}

/** 弹窗：在已选歌曲中选择合并目标（保留哪一条 Song） */
function pickMergeTargetMasterSong(ids) {
  const idSet = new Set(ids);
  const rows = (state.songs || []).filter((s) => idSet.has(s.id));
  if (rows.length < ids.length) {
    showToast("部分所选歌曲不在当前列表中，请先刷新后再试", "error");
    return Promise.resolve(null);
  }
  rows.sort((a, b) => a.id - b.id);

  return new Promise((resolve) => {
    const overlay = els.mergeTargetOverlay;
    const listEl = els.mergeTargetList;
    if (!overlay || !listEl) {
      showToast("合并弹窗未就绪", "error");
      resolve(null);
      return;
    }

    listEl.innerHTML = rows
      .map((s, i) => {
        const who = escapeHtml(s.lead_artist || s.artist || "—");
        const title = escapeHtml(s.title || "");
        const fmtList = Array.isArray(s.formats) && s.formats.length
          ? s.formats.map((f) => String(f || "").toUpperCase()).join(" / ")
          : s.file_format
            ? String(s.file_format).toUpperCase()
            : "—";
        const fmt = escapeHtml(fmtList);
        const created = escapeHtml(formatDate(s.created_at));
        return `<label class="merge-target-option">
  <input type="radio" name="mergeTargetMaster" value="${s.id}" ${i === 0 ? "checked" : ""} />
  <span class="merge-target-label">
    <span class="merge-target-line merge-target-title"><span class="merge-target-id">ID ${s.id}</span><span class="merge-target-song-title">${title}</span></span>
    <span class="merge-target-meta">
      <span class="merge-target-kv"><span class="merge-target-k">原唱</span><span class="merge-target-v">${who}</span></span>
      <span class="merge-target-kv"><span class="merge-target-k">格式</span><span class="merge-target-v">${fmt}</span></span>
      <span class="merge-target-kv"><span class="merge-target-k">创建时间</span><span class="merge-target-v">${created}</span></span>
    </span>
  </span>
</label>`;
      })
      .join("");

    const finish = (masterId) => {
      overlay.classList.add("hidden");
      els.mergeTargetConfirmBtn?.removeEventListener("click", onConfirm);
      els.mergeTargetCancelBtn?.removeEventListener("click", onCancel);
      els.mergeTargetCloseBtn?.removeEventListener("click", onCancel);
      overlay.removeEventListener("click", onBackdrop);
      resolve(masterId);
    };

    const onConfirm = () => {
      const r = listEl.querySelector('input[name="mergeTargetMaster"]:checked');
      finish(r ? Number(r.value) : null);
    };
    const onCancel = () => finish(null);
    const onBackdrop = (e) => {
      if (e.target === overlay) onCancel();
    };

    els.mergeTargetConfirmBtn?.addEventListener("click", onConfirm);
    els.mergeTargetCancelBtn?.addEventListener("click", onCancel);
    els.mergeTargetCloseBtn?.addEventListener("click", onCancel);
    overlay.addEventListener("click", onBackdrop);
    overlay.classList.remove("hidden");
  });
}

async function batchMergeSelectedSongs() {
  const ids = getSelectedSongIds();
  if (ids.length < 2) {
    showToast("请至少勾选 2 首歌曲", "error");
    return;
  }
  const masterId = await pickMergeTargetMasterSong(ids);
  if (masterId == null) return;

  try {
    const res = await request("/admin/songs/merge-selected", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ song_ids: ids, master_song_id: masterId }),
    });
    state.selectedSongs.clear();
    showToast(`已合并到歌曲 ID ${res.master_id}，并入 ${res.merged_slave_songs} 首其他曲目的音频（主曲元数据未改）`, "success");
    await Promise.all([loadSongs(), loadFilterOptions()]);
  } catch (err) {
    showToast(`合并失败: ${err.message || err}`, "error");
  }
}

async function batchDownloadSongs() {
  const ids = getSelectedSongIds();
  if (!ids.length) return;
  const songs = ids.map((id) => state.songs.find((s) => s.id === id)).filter(Boolean);
  if (songs.length !== ids.length) {
    showToast("部分所选歌曲不在当前列表，请刷新后重试", "error");
    return;
  }
  await startDownloadFlow(songs);
}

function createInlineManagerItem(itemData, type) {
  const item = document.createElement("article");
  item.className = "tag-manager-item";
  const typeLabel = type === "tag" ? "标签" : type === "language" ? "语言" : type === "genre" ? "风格" : "艺人";
  item.innerHTML = `
    <div class="tag-manager-main">
      <strong class="tag-display">${itemData.name}</strong>
      ${type === "person" ? `<p class="song-meta tag-type-text">${(itemData.types || []).join(" / ") || "歌手"}</p>` : ""}
    </div>
    <div class="variant-actions">
      <button class="btn" data-role="edit">修改</button>
      <button class="btn danger-text" data-role="delete">删除</button>
    </div>
  `;

  item.querySelector('[data-role="edit"]').addEventListener("click", () => {
    state.editModalType = type;
    state.editModalId = itemData.id;
    els.editModalTitle.textContent = `编辑${typeLabel}`;
    
    const editCard = els.itemEditOverlay?.querySelector(".modal-card");
    if (editCard) editCard.classList.toggle("modal-card-tall", type === "person");
    if (type === "person") {
      els.editFormBody.innerHTML = `
        <label class="form-field"><span>艺人名称</span><input type="text" id="editItemName" value="${itemData.name}" /></label>
        <div class="form-field"><span>类型</span><div id="editItemTypes" class="multi-select compact-multi-select"></div></div>
      `;
      const typesContainer = document.getElementById("editItemTypes");
      if (typesContainer) renderTypeMultiSelect(typesContainer, itemData.types || ["歌手"]);
    } else {
      els.editFormBody.innerHTML = `<label class="form-field"><span>${typeLabel}名称</span><input type="text" id="editItemName" value="${itemData.name}" /></label>`;
    }
    
    els.itemEditOverlay.classList.remove("hidden");
  });

  item.querySelector('[data-role="delete"]').addEventListener("click", () => {
    state.deleteModalType = type;
    state.deleteModalId = itemData.id;
    els.deleteMessage.textContent = `确认删除该${typeLabel}「${itemData.name}」吗？`;
    els.deleteOverlay.classList.remove("hidden");
  });

  return item;
}

function closeItemEditModal() {
  const editCard = els.itemEditOverlay?.querySelector(".modal-card");
  if (editCard) editCard.classList.remove("modal-card-tall");
  els.itemEditOverlay.classList.add("hidden");
  state.editModalType = null;
  state.editModalId = null;
}

async function submitEditForm(e) {
  e.preventDefault();
  const type = state.editModalType;
  const id = state.editModalId;
  if (!type || !id) return;
  
  const nameInput = document.getElementById("editItemName");
  const name = nameInput?.value?.trim() || "";
  if (!name) return;
  
  const path = type === "tag" ? `/tags/${id}` : type === "language" ? `/languages/${id}` : type === "genre" ? `/genres/${id}` : `/people/${id}`;
  let body = { name };
  if (type === "person") {
    const typesContainer = document.getElementById("editItemTypes");
    body.types = getSelectedTypes(typesContainer).length ? getSelectedTypes(typesContainer) : ["歌手"];
  }
  
  await request(path, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  
  closeItemEditModal();
  if (type === "tag") {
    await Promise.all([loadTags(), loadFilterOptions(), loadSongs()]);
    showToast("标签已更新", "success");
  } else if (type === "language") {
    await Promise.all([loadLanguages(), loadFilterOptions(), loadSongs()]);
    showToast("语言已更新", "success");
  } else if (type === "genre") {
    await loadGenres();
    showToast("风格已更新", "success");
  } else {
    await Promise.all([loadPeople(), loadSongs()]);
    showToast("艺人已更新", "success");
  }
}

function closeDeleteModal() {
  els.deleteOverlay.classList.add("hidden");
  state.deleteModalType = null;
  state.deleteModalId = null;
  state.batchDeleteIds = [];
  state.batchDeleteManager = null;
}

function openDeleteModal(type, id) {
  const typeLabel = type === "tag" ? "标签" : type === "language" ? "语言" : type === "genre" ? "风格" : "艺人";
  const item = type === "tag" ? state.tags?.find(t => t.id === id) :
               type === "language" ? state.languages?.find(l => l.id === id) :
               type === "genre" ? state.genres?.find(g => g.id === id) :
               state.people?.find(p => p.id === id);
  state.deleteModalType = type;
  state.deleteModalId = id;
  els.deleteMessage.textContent = `确认删除该${typeLabel}「${item?.name || ''}」吗？`;
  els.deleteOverlay.classList.remove("hidden");
}

function getDeletePath(manager, id) {
  return manager === "tag" ? `/tags/${id}` : manager === "language" ? `/languages/${id}` : manager === "genre" ? `/genres/${id}` : `/people/${id}`;
}

function updateManagerBatchButton(manager) {
  const set = state[manager === "people" ? "selectedPeople" : manager === "tag" ? "selectedTags" : manager === "language" ? "selectedLanguages" : "selectedGenres"];
  const btn = manager === "people" ? els.peopleBatchDeleteBtn : manager === "tag" ? els.tagBatchDeleteBtn : manager === "language" ? els.languageBatchDeleteBtn : els.genreBatchDeleteBtn;
  if (btn) btn.classList.toggle("hidden", set.size === 0);
}

async function confirmDelete() {
  if (state.batchDeleteIds && state.batchDeleteIds.length > 0) {
    const manager = state.batchDeleteManager;
    const label = manager === "people" ? "艺人" : manager === "tag" ? "标签" : manager === "language" ? "语言" : "风格";
    for (const id of state.batchDeleteIds) {
      await request(getDeletePath(manager, id), { method: "DELETE" });
    }
    if (manager === "people") {
      state.selectedPeople.clear();
      await Promise.all([loadPeople(), loadFilterOptions(), loadSongs()]);
    } else if (manager === "tag") {
      state.selectedTags.clear();
      await Promise.all([loadTags(), loadFilterOptions(), loadSongs()]);
    } else if (manager === "language") {
      state.selectedLanguages.clear();
      await Promise.all([loadLanguages(), loadFilterOptions(), loadSongs()]);
    } else {
      state.selectedGenres.clear();
      await loadGenres();
    }
    showToast(`已删除 ${state.batchDeleteIds.length} 个${label}`, "success");
    state.batchDeleteIds = [];
    state.batchDeleteManager = null;
    closeDeleteModal();
    return;
  }

  const type = state.deleteModalType;
  const id = state.deleteModalId;
  if (!type || !id) return;

  await request(getDeletePath(type, id), { method: "DELETE" });

  closeDeleteModal();
  if (type === "tag") {
    await Promise.all([loadTags(), loadFilterOptions(), loadSongs()]);
    showToast("标签已删除", "success");
  } else if (type === "language") {
    await Promise.all([loadLanguages(), loadFilterOptions(), loadSongs()]);
    showToast("语言已删除", "success");
  } else if (type === "genre") {
    await loadGenres();
    showToast("风格已删除", "success");
  } else {
    await Promise.all([loadPeople(), loadSongs()]);
    showToast("艺人已删除", "success");
  }
}

function sortManagerList(list, sortBy, sortOrder, managerType) {
  const dir = sortOrder === "asc" ? 1 : -1;
  return [...list].sort((a, b) => {
    let va = a[sortBy];
    let vb = b[sortBy];
    if (sortBy === "types" && managerType === "people") {
      va = (a.types || []).join(" / ") || "";
      vb = (b.types || []).join(" / ") || "";
    }
    if (sortBy === "name") {
      return dir * (String(va || "").localeCompare(String(vb || ""), "zh-CN"));
    }
    if (sortBy === "created_at") {
      return dir * (String(va || "").localeCompare(String(vb || "")));
    }
    return dir * (String(va || "").localeCompare(String(vb || ""), "zh-CN"));
  });
}

function updateManagerSortIndicators(manager) {
  const pageId = { people: "people", tag: "tags", language: "language", genre: "genre" }[manager];
  const pageEl = document.getElementById(`admin-page-${pageId}`);
  if (!pageEl) return;
  const sortBy = state[`${manager}SortBy`];
  const sortOrder = state[`${manager}SortOrder`];
  pageEl.querySelectorAll(".manager-sort-btn").forEach((btn) => {
    const label = btn.dataset.label || btn.textContent.replace(/ [↑↓]$/, "");
    const arrow = btn.dataset.sort === sortBy ? (sortOrder === "asc" ? " ↑" : " ↓") : "";
    btn.textContent = label + arrow;
  });
}

function renderTagManager() {
  if (!els.tagTableBody || !els.tagSearchInput) return;
  const keyword = (els.tagSearchInput.value || "").trim().toLowerCase();
  let tags = (state.tags || []).filter((tag) => !keyword || (tag.name || "").toLowerCase().includes(keyword));
  tags = sortManagerList(tags, state.tagSortBy, state.tagSortOrder, "tag");
  if (!tags.length) {
    els.tagTableBody.innerHTML = '<tr><td colspan="5" class="empty-cell">暂无标签</td></tr>';
  } else {
    els.tagTableBody.innerHTML = tags.map((tag, index) => `
      <tr data-id="${tag.id}">
        <td><input type="checkbox" class="manager-row-checkbox" data-manager="tag" data-id="${tag.id}" ${state.selectedTags.has(tag.id) ? "checked" : ""} /></td>
        <td>${index + 1}</td>
        <td><strong>${tag.name}</strong></td>
        <td>${tag.created_at || "-"}</td>
        <td>
          <button class="btn btn-sm" data-role="edit" data-id="${tag.id}">修改</button>
          <button class="btn btn-sm danger-text" data-role="delete" data-id="${tag.id}">删除</button>
        </td>
      </tr>
    `).join("");
    els.tagTableBody.querySelectorAll("[data-role='edit']").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id);
        const tag = state.tags.find(t => t.id === id);
        if (tag) openCreateModal("tag", tag);
      });
    });
    els.tagTableBody.querySelectorAll("[data-role='delete']").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id);
        openDeleteModal("tag", id);
      });
    });
    els.tagTableBody.querySelectorAll(".manager-row-checkbox").forEach((cb) => {
      cb.addEventListener("change", () => {
        const id = parseInt(cb.dataset.id);
        if (cb.checked) state.selectedTags.add(id); else state.selectedTags.delete(id);
        updateManagerBatchButton("tag");
      });
    });
  }
  const visibleTagIds = tags.map((t) => t.id);
  if (els.selectAllTags) {
    els.selectAllTags.checked = visibleTagIds.length > 0 && visibleTagIds.every((id) => state.selectedTags.has(id));
    els.selectAllTags.indeterminate = visibleTagIds.some((id) => state.selectedTags.has(id)) && !els.selectAllTags.checked;
  }
  updateManagerBatchButton("tag");
}

function renderLanguageManager() {
  if (!els.languageTableBody || !els.languageSearchInput) return;
  const keyword = (els.languageSearchInput.value || "").trim().toLowerCase();
  let languages = (state.languages || []).filter((language) => !keyword || (language.name || "").toLowerCase().includes(keyword));
  languages = sortManagerList(languages, state.languageSortBy, state.languageSortOrder, "language");
  if (!languages.length) {
    els.languageTableBody.innerHTML = '<tr><td colspan="5" class="empty-cell">暂无语言</td></tr>';
  } else {
    els.languageTableBody.innerHTML = languages.map((language, index) => `
      <tr data-id="${language.id}">
        <td><input type="checkbox" class="manager-row-checkbox" data-manager="language" data-id="${language.id}" ${state.selectedLanguages.has(language.id) ? "checked" : ""} /></td>
        <td>${index + 1}</td>
        <td><strong>${language.name}</strong></td>
        <td>${language.created_at || "-"}</td>
        <td>
          <button class="btn btn-sm" data-role="edit" data-id="${language.id}">修改</button>
          <button class="btn btn-sm danger-text" data-role="delete" data-id="${language.id}">删除</button>
        </td>
      </tr>
    `).join("");
    els.languageTableBody.querySelectorAll("[data-role='edit']").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id);
        const language = state.languages.find(l => l.id === id);
        if (language) openCreateModal("language", language);
      });
    });
    els.languageTableBody.querySelectorAll("[data-role='delete']").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id);
        openDeleteModal("language", id);
      });
    });
    els.languageTableBody.querySelectorAll(".manager-row-checkbox").forEach((cb) => {
      cb.addEventListener("change", () => {
        const id = parseInt(cb.dataset.id);
        if (cb.checked) state.selectedLanguages.add(id); else state.selectedLanguages.delete(id);
        updateManagerBatchButton("language");
      });
    });
  }
  const visibleLanguageIds = languages.map((l) => l.id);
  if (els.selectAllLanguages) {
    els.selectAllLanguages.checked = visibleLanguageIds.length > 0 && visibleLanguageIds.every((id) => state.selectedLanguages.has(id));
    els.selectAllLanguages.indeterminate = visibleLanguageIds.some((id) => state.selectedLanguages.has(id)) && !els.selectAllLanguages.checked;
  }
  updateManagerBatchButton("language");
}

function renderPeopleManager() {
  if (!els.peopleTableBody || !els.peopleSearchInput) return;
  const keyword = (els.peopleSearchInput.value || "").trim().toLowerCase();
  let people = (state.people || []).filter((person) => !keyword || (person.name || "").toLowerCase().includes(keyword));
  people = sortManagerList(people, state.peopleSortBy, state.peopleSortOrder, "people");
  if (!people.length) {
    els.peopleTableBody.innerHTML = '<tr><td colspan="6" class="empty-cell">暂无艺人</td></tr>';
  } else {
    els.peopleTableBody.innerHTML = people.map((person, index) => `
      <tr data-id="${person.id}">
        <td><input type="checkbox" class="manager-row-checkbox" data-manager="people" data-id="${person.id}" ${state.selectedPeople.has(person.id) ? "checked" : ""} /></td>
        <td>${index + 1}</td>
        <td><strong>${person.name}</strong></td>
        <td>${(person.types || []).join(" / ") || "歌手"}</td>
        <td>${person.created_at || "-"}</td>
        <td>
          <button class="btn btn-sm" data-role="edit" data-id="${person.id}">修改</button>
          <button class="btn btn-sm danger-text" data-role="delete" data-id="${person.id}">删除</button>
        </td>
      </tr>
    `).join("");
    els.peopleTableBody.querySelectorAll("[data-role='edit']").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id);
        const person = state.people.find(p => p.id === id);
        if (person) openCreateModal("person", person);
      });
    });
    els.peopleTableBody.querySelectorAll("[data-role='delete']").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id);
        openDeleteModal("person", id);
      });
    });
    els.peopleTableBody.querySelectorAll(".manager-row-checkbox").forEach((cb) => {
      cb.addEventListener("change", () => {
        const id = parseInt(cb.dataset.id);
        if (cb.checked) state.selectedPeople.add(id); else state.selectedPeople.delete(id);
        updateManagerBatchButton("people");
      });
    });
  }
  const visiblePeopleIds = people.map((p) => p.id);
  if (els.selectAllPeople) {
    els.selectAllPeople.checked = visiblePeopleIds.length > 0 && visiblePeopleIds.every((id) => state.selectedPeople.has(id));
    els.selectAllPeople.indeterminate = visiblePeopleIds.some((id) => state.selectedPeople.has(id)) && !els.selectAllPeople.checked;
  }
  updateManagerBatchButton("people");
}

async function loadFilterOptions() {
  try {
    state.filters = await request("/admin/filter-options");
  } catch (err) {
    state.filters = { formats: [], lead_artists: [], tags: [], languages: [], lyricists: [], composers: [], genres: [] };
    showToast("加载筛选选项失败: " + (err && err.message ? err.message : String(err)), "error");
  }
}

async function loadTags() {
  try {
    state.tags = await request("/tags");
  } catch (err) {
    state.tags = [];
    showToast("加载标签失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  renderTagMultiSelect(state.editingSongId ? getSelectedTagIds() : []);
  renderTagManager();
  updateManagerSortIndicators("tag");
  populateQuickFilterOptions();
}

async function loadLanguages() {
  try {
    state.languages = await request("/languages");
  } catch (err) {
    state.languages = [];
    showToast("加载语言失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  renderLanguageMultiSelect(state.editingSongId ? getSelectedLanguageIds() : []);
  renderLanguageManager();
  updateManagerSortIndicators("language");
  populateQuickFilterOptions();
}

function renderLanguageMultiSelect(selectedIds = []) {
  if (!els.languageInput) return;
  const langs = state.languages || [];
  const validSelectedIds = selectedIds.filter((id) => langs.some((l) => l.id === id));
  const container = els.languageInput;
  container._searchText = "";
  container._languageSelectedIds = new Set(validSelectedIds);

  container.innerHTML = `
    <div class="multi-select-trigger" role="button" tabindex="0">请选择语言</div>
    <div class="multi-select-menu hidden">
      <input type="text" class="multi-select-search" placeholder="搜索、筛选或输入新语言…" autocomplete="off" />
      <div class="multi-select-options"></div>
    </div>
  `;
  const trigger = container.querySelector(".multi-select-trigger");
  const menu = container.querySelector(".multi-select-menu");
  const searchInput = menu.querySelector(".multi-select-search");
  const optionsEl = menu.querySelector(".multi-select-options");

  const updateTrigger = () => {
    const names = Array.from(container._languageSelectedIds)
      .map((id) => langs.find((l) => l.id === id)?.name)
      .filter(Boolean);
    trigger.innerHTML = names.length
      ? `<span class="tag-list">${names.map((n) => `<span class="tag">${escapeHtmlUserText(n)}</span>`).join("")}</span>`
      : "请选择语言";
  };

  const metaRowHtml = (kwRaw) => {
    const kw = kwRaw.trim();
    if (!kw) return "";
    const lower = kw.toLowerCase();
    const exact = langs.find((l) => (l.name || "").trim().toLowerCase() === lower);
    if (exact) return "";
    return `<div class="multi-select-meta-hint">无完全匹配时可新建：</div>
      <div class="multi-select-meta-row" tabindex="0" role="button" data-action="create-lang">
        创建并添加「${escapeHtmlUserText(kw)}」
      </div>`;
  };

  const rebuildOptions = () => {
    const kw = (container._searchText || "").trim();
    const sel = container._languageSelectedIds;
    const sorted = sortByRecentName(langs, LANGUAGE_RECENT_KEY);
    const list = !kw ? sorted : sorted.filter((l) => fuzzyMatchName(l.name, kw) || sel.has(l.id));
    const meta = metaRowHtml(container._searchText || "");
    let body = meta;
    if (list.length) {
      body += list
        .map(
          (l) =>
            `<div class="artist-option"><input type="checkbox" value="${l.id}" ${sel.has(l.id) ? "checked" : ""} /><span>${escapeHtmlUserText(l.name)}</span></div>`,
        )
        .join("");
    }
    if (!list.length && !meta) {
      body += '<div class="multi-select-empty muted" style="padding:10px 8px;font-size:13px;">无匹配结果</div>';
    }
    optionsEl.innerHTML = body;
  };

  const setMetaBusy = (busy) => {
    menu.querySelectorAll(".multi-select-meta-row").forEach((el) => el.classList.toggle("is-busy", busy));
  };

  menu.addEventListener("click", async (e) => {
    const row = e.target.closest('.multi-select-meta-row[data-action="create-lang"]');
    if (!row) return;
    e.preventDefault();
    e.stopPropagation();
    const kw = (container._searchText || "").trim();
    if (!kw) return;
    try {
      setMetaBusy(true);
      const created = await request("/languages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: kw }),
      });
      if (!state.languages) state.languages = [];
      state.languages.push(created);
      state.languages.sort((a, b) => (a.name || "").localeCompare(b.name || "", "zh-CN"));
      touchLanguageRecent(created.id);
      container._languageSelectedIds.add(created.id);
      container._searchText = "";
      if (searchInput) searchInput.value = "";
      await loadFilterOptions();
      updateTrigger();
      rebuildOptions();
      showToast("已添加语言", "success");
    } catch (err) {
      showToast(err.message || String(err), "error");
    } finally {
      setMetaBusy(false);
    }
  });

  updateTrigger();
  rebuildOptions();

  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (activeMultiSelect && activeMultiSelect !== menu) activeMultiSelect.classList.add("hidden");
    const willOpen = menu.classList.contains("hidden");
    menu.classList.toggle("hidden", !willOpen);
    activeMultiSelect = willOpen ? menu : null;
    if (willOpen) setTimeout(() => searchInput?.focus(), 0);
  });
  searchInput?.addEventListener("click", (ev) => ev.stopPropagation());
  searchInput?.addEventListener("keydown", (ev) => {
    if (ev.key !== "Enter") return;
    ev.preventDefault();
    ev.stopPropagation();
    const createEl = menu.querySelector('.multi-select-meta-row[data-action="create-lang"]');
    if (createEl) createEl.click();
  });
  searchInput?.addEventListener("input", (event) => {
    container._searchText = event.target.value;
    rebuildOptions();
  });
  attachMultiSelectOptionRowClick(menu);
  menu.addEventListener("change", (event) => {
    if (event.target.type === "checkbox") {
      const id = Number(event.target.value);
      if (event.target.checked) {
        container._languageSelectedIds.add(id);
        touchLanguageRecent(id);
      } else container._languageSelectedIds.delete(id);
      updateTrigger();
    }
  });
}

function getSelectedLanguageIds() {
  if (!els.languageInput) return [];
  if (els.languageInput._languageSelectedIds instanceof Set) return Array.from(els.languageInput._languageSelectedIds);
  return Array.from(els.languageInput.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => Number(cb.value));
}

function renderTagMultiSelect(selectedIds = []) {
  if (!els.tagInput) return;
  const tags = state.tags || [];
  const validSelectedIds = selectedIds.filter((id) => tags.some((t) => t.id === id));
  const container = els.tagInput;
  container._searchText = "";
  container._tagSelectedIds = new Set(validSelectedIds);

  container.innerHTML = `
    <div class="multi-select-trigger" role="button" tabindex="0">请选择标签</div>
    <div class="multi-select-menu hidden">
      <input type="text" class="multi-select-search" placeholder="搜索、筛选或输入新标签…" autocomplete="off" />
      <div class="multi-select-options"></div>
    </div>
  `;
  const trigger = container.querySelector(".multi-select-trigger");
  const menu = container.querySelector(".multi-select-menu");
  const searchInput = menu.querySelector(".multi-select-search");
  const optionsEl = menu.querySelector(".multi-select-options");

  const updateTrigger = () => {
    const names = Array.from(container._tagSelectedIds)
      .map((id) => tags.find((t) => t.id === id)?.name)
      .filter(Boolean);
    trigger.innerHTML = names.length
      ? `<span class="tag-list">${names.map((n) => `<span class="tag">${escapeHtmlUserText(n)}</span>`).join("")}</span>`
      : "请选择标签";
  };

  const metaRowHtml = (kwRaw) => {
    const kw = kwRaw.trim();
    if (!kw) return "";
    const lower = kw.toLowerCase();
    const exact = tags.find((t) => (t.name || "").trim().toLowerCase() === lower);
    if (exact) return "";
    return `<div class="multi-select-meta-hint">无完全匹配时可新建：</div>
      <div class="multi-select-meta-row" tabindex="0" role="button" data-action="create-tag">
        创建并添加「${escapeHtmlUserText(kw)}」
      </div>`;
  };

  const rebuildOptions = () => {
    const kw = (container._searchText || "").trim();
    const sel = container._tagSelectedIds;
    const sorted = sortByRecentName(tags, TAG_RECENT_KEY);
    const list = !kw ? sorted : sorted.filter((t) => fuzzyMatchName(t.name, kw) || sel.has(t.id));
    const meta = metaRowHtml(container._searchText || "");
    let body = meta;
    if (list.length) {
      body += list
        .map(
          (t) =>
            `<div class="artist-option"><input type="checkbox" value="${t.id}" ${sel.has(t.id) ? "checked" : ""} /><span>${escapeHtmlUserText(t.name)}</span></div>`,
        )
        .join("");
    }
    if (!list.length && !meta) {
      body += '<div class="multi-select-empty muted" style="padding:10px 8px;font-size:13px;">无匹配结果</div>';
    }
    optionsEl.innerHTML = body;
  };

  const setMetaBusy = (busy) => {
    menu.querySelectorAll(".multi-select-meta-row").forEach((el) => el.classList.toggle("is-busy", busy));
  };

  menu.addEventListener("click", async (e) => {
    const row = e.target.closest('.multi-select-meta-row[data-action="create-tag"]');
    if (!row) return;
    e.preventDefault();
    e.stopPropagation();
    const kw = (container._searchText || "").trim();
    if (!kw) return;
    try {
      setMetaBusy(true);
      const created = await request("/tags", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: kw }),
      });
      if (!state.tags) state.tags = [];
      state.tags.push(created);
      state.tags.sort((a, b) => (a.name || "").localeCompare(b.name || "", "zh-CN"));
      touchTagRecent(created.id);
      container._tagSelectedIds.add(created.id);
      container._searchText = "";
      if (searchInput) searchInput.value = "";
      populateQuickFilterOptions();
      renderTagManager();
      updateTrigger();
      rebuildOptions();
      showToast("已添加标签", "success");
    } catch (err) {
      showToast(err.message || String(err), "error");
    } finally {
      setMetaBusy(false);
    }
  });

  updateTrigger();
  rebuildOptions();

  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (activeMultiSelect && activeMultiSelect !== menu) activeMultiSelect.classList.add("hidden");
    const willOpen = menu.classList.contains("hidden");
    menu.classList.toggle("hidden", !willOpen);
    activeMultiSelect = willOpen ? menu : null;
    if (willOpen) setTimeout(() => searchInput?.focus(), 0);
  });
  searchInput?.addEventListener("click", (ev) => ev.stopPropagation());
  searchInput?.addEventListener("keydown", (ev) => {
    if (ev.key !== "Enter") return;
    ev.preventDefault();
    ev.stopPropagation();
    const createEl = menu.querySelector('.multi-select-meta-row[data-action="create-tag"]');
    if (createEl) createEl.click();
  });
  searchInput?.addEventListener("input", (event) => {
    container._searchText = event.target.value;
    rebuildOptions();
  });
  attachMultiSelectOptionRowClick(menu);
  menu.addEventListener("change", (event) => {
    if (event.target.type === "checkbox") {
      const id = Number(event.target.value);
      if (event.target.checked) {
        container._tagSelectedIds.add(id);
        touchTagRecent(id);
      } else container._tagSelectedIds.delete(id);
      updateTrigger();
    }
  });
}

function getSelectedTagIds() {
  if (!els.tagInput) return [];
  if (els.tagInput._tagSelectedIds instanceof Set) return Array.from(els.tagInput._tagSelectedIds);
  return Array.from(els.tagInput.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => Number(cb.value));
}

function renderGenreMultiSelect(selectedIds = []) {
  if (!els.genreInput) return;
  const genres = state.genres || [];
  const validSelectedIds = selectedIds.filter((id) => genres.some((g) => g.id === id));
  const container = els.genreInput;
  container._searchText = "";
  container._genreSelectedIds = new Set(validSelectedIds);

  container.innerHTML = `
    <div class="multi-select-trigger" role="button" tabindex="0">请选择风格</div>
    <div class="multi-select-menu hidden">
      <input type="text" class="multi-select-search" placeholder="搜索、筛选或输入新风格…" autocomplete="off" />
      <div class="multi-select-options"></div>
    </div>
  `;
  const trigger = container.querySelector(".multi-select-trigger");
  const menu = container.querySelector(".multi-select-menu");
  const searchInput = menu.querySelector(".multi-select-search");
  const optionsEl = menu.querySelector(".multi-select-options");

  const updateTrigger = () => {
    const names = Array.from(container._genreSelectedIds)
      .map((id) => genres.find((g) => g.id === id)?.name)
      .filter(Boolean);
    trigger.innerHTML = names.length
      ? `<span class="tag-list">${names.map((n) => `<span class="tag">${escapeHtmlUserText(n)}</span>`).join("")}</span>`
      : "请选择风格";
  };

  const metaRowHtml = (kwRaw) => {
    const kw = kwRaw.trim();
    if (!kw) return "";
    const lower = kw.toLowerCase();
    const exact = genres.find((g) => (g.name || "").trim().toLowerCase() === lower);
    if (exact) return "";
    return `<div class="multi-select-meta-hint">无完全匹配时可新建：</div>
      <div class="multi-select-meta-row" tabindex="0" role="button" data-action="create-genre">
        创建并添加「${escapeHtmlUserText(kw)}」
      </div>`;
  };

  const rebuildOptions = () => {
    const kw = (container._searchText || "").trim();
    const sel = container._genreSelectedIds;
    const sorted = sortByRecentName(genres, GENRE_RECENT_KEY);
    const list = !kw ? sorted : sorted.filter((g) => fuzzyMatchName(g.name, kw) || sel.has(g.id));
    const meta = metaRowHtml(container._searchText || "");
    let body = meta;
    if (list.length) {
      body += list
        .map(
          (g) =>
            `<div class="artist-option"><input type="checkbox" value="${g.id}" ${sel.has(g.id) ? "checked" : ""} /><span>${escapeHtmlUserText(g.name)}</span></div>`,
        )
        .join("");
    }
    if (!list.length && !meta) {
      body += '<div class="multi-select-empty muted" style="padding:10px 8px;font-size:13px;">无匹配结果</div>';
    }
    optionsEl.innerHTML = body;
  };

  const setMetaBusy = (busy) => {
    menu.querySelectorAll(".multi-select-meta-row").forEach((el) => el.classList.toggle("is-busy", busy));
  };

  menu.addEventListener("click", async (e) => {
    const row = e.target.closest('.multi-select-meta-row[data-action="create-genre"]');
    if (!row) return;
    e.preventDefault();
    e.stopPropagation();
    const kw = (container._searchText || "").trim();
    if (!kw) return;
    try {
      setMetaBusy(true);
      const created = await request("/genres", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: kw }),
      });
      if (!state.genres) state.genres = [];
      state.genres.push(created);
      state.genres.sort((a, b) => (a.name || "").localeCompare(b.name || "", "zh-CN"));
      touchGenreRecent(created.id);
      container._genreSelectedIds.add(created.id);
      container._searchText = "";
      if (searchInput) searchInput.value = "";
      await loadFilterOptions();
      updateTrigger();
      rebuildOptions();
      showToast("已添加风格", "success");
    } catch (err) {
      showToast(err.message || String(err), "error");
    } finally {
      setMetaBusy(false);
    }
  });

  updateTrigger();
  rebuildOptions();

  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (activeMultiSelect && activeMultiSelect !== menu) activeMultiSelect.classList.add("hidden");
    const willOpen = menu.classList.contains("hidden");
    menu.classList.toggle("hidden", !willOpen);
    activeMultiSelect = willOpen ? menu : null;
    if (willOpen) setTimeout(() => searchInput?.focus(), 0);
  });
  searchInput?.addEventListener("click", (ev) => ev.stopPropagation());
  searchInput?.addEventListener("keydown", (ev) => {
    if (ev.key !== "Enter") return;
    ev.preventDefault();
    ev.stopPropagation();
    const createEl = menu.querySelector('.multi-select-meta-row[data-action="create-genre"]');
    if (createEl) createEl.click();
  });
  searchInput?.addEventListener("input", (event) => {
    container._searchText = event.target.value;
    rebuildOptions();
  });
  attachMultiSelectOptionRowClick(menu);
  menu.addEventListener("change", (event) => {
    if (event.target.type === "checkbox") {
      const id = Number(event.target.value);
      if (event.target.checked) {
        container._genreSelectedIds.add(id);
        touchGenreRecent(id);
      } else container._genreSelectedIds.delete(id);
      updateTrigger();
    }
  });
}

function getSelectedGenreIds() {
  if (!els.genreInput) return [];
  if (els.genreInput._genreSelectedIds instanceof Set) return Array.from(els.genreInput._genreSelectedIds);
  return Array.from(els.genreInput.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => Number(cb.value));
}

async function loadGenres() {
  try {
    state.genres = await request("/genres");
  } catch (err) {
    state.genres = [];
    showToast("加载风格失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  renderGenreMultiSelect(state.editingSongId ? getSelectedGenreIds() : []);
  renderGenreManager();
  updateManagerSortIndicators("genre");
  populateQuickFilterOptions();
}

function renderGenreManager() {
  if (!els.genreTableBody || !els.genreSearchInput) return;
  const keyword = (els.genreSearchInput.value || "").trim().toLowerCase();
  let genres = (state.genres || []).filter((g) => !keyword || (g.name || "").toLowerCase().includes(keyword));
  genres = sortManagerList(genres, state.genreSortBy, state.genreSortOrder, "genre");
  if (!genres.length) {
    els.genreTableBody.innerHTML = '<tr><td colspan="5" class="empty-cell">暂无风格</td></tr>';
  } else {
    els.genreTableBody.innerHTML = genres.map((g, index) => `
      <tr data-id="${g.id}">
        <td><input type="checkbox" class="manager-row-checkbox" data-manager="genre" data-id="${g.id}" ${state.selectedGenres.has(g.id) ? "checked" : ""} /></td>
        <td>${index + 1}</td>
        <td><strong>${g.name}</strong></td>
        <td>${g.created_at || "-"}</td>
        <td>
          <button class="btn btn-sm" data-role="edit" data-id="${g.id}">修改</button>
          <button class="btn btn-sm danger-text" data-role="delete" data-id="${g.id}">删除</button>
        </td>
      </tr>
    `).join("");
    els.genreTableBody.querySelectorAll("[data-role='edit']").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id);
        const genre = state.genres.find(g => g.id === id);
        if (genre) openCreateModal("genre", genre);
      });
    });
    els.genreTableBody.querySelectorAll("[data-role='delete']").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.dataset.id);
        openDeleteModal("genre", id);
      });
    });
    els.genreTableBody.querySelectorAll(".manager-row-checkbox").forEach((cb) => {
      cb.addEventListener("change", () => {
        const id = parseInt(cb.dataset.id);
        if (cb.checked) state.selectedGenres.add(id); else state.selectedGenres.delete(id);
        updateManagerBatchButton("genre");
      });
    });
  }
  const visibleGenreIds = genres.map((g) => g.id);
  if (els.selectAllGenres) {
    els.selectAllGenres.checked = visibleGenreIds.length > 0 && visibleGenreIds.every((id) => state.selectedGenres.has(id));
    els.selectAllGenres.indeterminate = visibleGenreIds.some((id) => state.selectedGenres.has(id)) && !els.selectAllGenres.checked;
  }
  updateManagerBatchButton("genre");
}

async function loadPeople() {
  try {
    state.people = await request("/people");
  } catch (err) {
    state.people = [];
    showToast("加载艺人失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  if (els.leadArtistInput) renderArtistMultiSelect(els.leadArtistInput, getSelectedArtistIds(els.leadArtistInput));
  if (els.lyricistInput) renderArtistMultiSelect(els.lyricistInput, getSelectedArtistIds(els.lyricistInput), "作词");
  if (els.composerInput) renderArtistMultiSelect(els.composerInput, getSelectedArtistIds(els.composerInput), "作曲");
  renderPeopleManager();
  updateManagerSortIndicators("people");
  populateQuickFilterOptions();
}

function resetAdminSongListFilters() {
  state.selectedSongs.clear();
  if (els.keywordInput) els.keywordInput.value = "";
  if (els.keywordClearBtn) els.keywordClearBtn.classList.add("hidden");
  state.quickFilterLeads = [];
  state.quickFilterLyricists = [];
  state.quickFilterComposers = [];
  state.quickFilterTags = [];
  state.quickFilterFormats = [];
  state.quickFilterLanguages = [];
  state.quickFilterGenres = [];
  ADMIN_QUICK_FILTER_SELECTS().forEach((selectEl) => {
    Array.from(selectEl.options).forEach((o) => {
      o.selected = false;
    });
    if (selectEl.dataset.searchableBound === "1") refreshSearchableSelectOptions(selectEl);
    syncSearchableSelectTrigger(selectEl);
  });
  state.songPage = 1;
  state.sortBy = "created_at";
  state.sortOrder = "desc";
  renderSortIndicators();
  loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
}

async function loadSongs() {
  syncQuickFiltersFromUi();
  updateBatchButtons();
  try {
    const page = await request(`/songs?${buildSongListQueryParams().toString()}`);
    state.songs = page.items || [];
    state.songListTotal = page.total ?? 0;
    state.songLibraryTotal = page.library_total ?? 0;
  } catch (err) {
    state.songs = [];
    state.songListTotal = 0;
    state.songLibraryTotal = 0;
    showToast("加载歌曲失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  populateQuickFilterOptions();
  renderSongs();
  updateAdminMusicResetVisibility();
}

async function runScan() {
  const selectedFiles = Array.from(els.directoryPicker.files || []);
  if (!selectedFiles.length) return;
  
  await request("/admin/scan-progress/reset", { method: "POST" });
  
  els.scanBtn.disabled = true;
  els.scanBtn.textContent = "扫描中...";
  els.scanProgressWrap.classList.remove("hidden");
  els.scanSummary.classList.add("hidden");
  els.scanProgressFill.style.width = "0%";
  els.scanProgressText.textContent = "正在初始化...";
  els.scanProgressStats.textContent = "准备中...";
  els.scanElapsedTime.textContent = "已耗时: 0秒";
  els.scanEstimatedTime.textContent = "预计剩余: --";
  
  state.scanProgressTimer = setInterval(pollScanProgress, 300);
  
  try {
    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("files", file, file.webkitRelativePath || file.name));
    
    await request("/admin/import-directory", {
      method: "POST",
      body: formData,
    });
    
    const finalProgress = await request("/admin/scan-progress");
    const elapsed = finalProgress.start_time ? Math.floor((Date.now() / 1000) - finalProgress.start_time) : 0;
    const elapsedStr = elapsed < 60 ? `${elapsed}秒` : `${Math.floor(elapsed / 60)}分${elapsed % 60}秒`;
    
    for (let i = 0; i < 5; i++) {
      await pollScanProgress();
      await new Promise(r => setTimeout(r, 200));
    }
    
    els.scanProgressWrap.classList.add("hidden");
    els.scanSummary.classList.remove("hidden");
    els.scanSummary.textContent = `扫描完成，总共${finalProgress.total_count}个文件，新增${finalProgress.added_count}个文件，跳过${finalProgress.skipped_count}个文件，总耗时${elapsedStr}`;
    await Promise.all([loadFilterOptions(), loadSongs()]);
    showToast("扫描完成", "success");
    if (
      finalProgress.skipped_count > 0 &&
      Array.isArray(finalProgress.skipped_details) &&
      finalProgress.skipped_details.length
    ) {
      showSkippedFilesModal(finalProgress.skipped_details);
    }
  } catch (err) {
    showToast(`扫描失败: ${err.message}`, "error");
  } finally {
    if (state.scanProgressTimer) {
      clearInterval(state.scanProgressTimer);
      state.scanProgressTimer = null;
    }
    els.scanBtn.disabled = false;
    els.scanBtn.textContent = "扫描目录";
    els.directoryPicker.value = "";
    els.scanProgressWrap.classList.add("hidden");
    els.scanSummary.classList.remove("hidden");
  }
}

async function addSongs() {
  const selectedFiles = Array.from(els.songFilePicker.files || []);
  if (!selectedFiles.length) return;
  
  await request("/admin/scan-progress/reset", { method: "POST" });
  
  els.addSongsBtn.disabled = true;
  els.addSongsBtn.textContent = "添加中...";
  els.scanProgressWrap.classList.remove("hidden");
  els.scanSummary.classList.add("hidden");
  els.scanProgressFill.style.width = "0%";
  els.scanProgressText.textContent = "正在初始化...";
  els.scanProgressStats.textContent = "准备中...";
  els.scanElapsedTime.textContent = "已耗时: 0秒";
  els.scanEstimatedTime.textContent = "预计剩余: --";
  
  state.scanProgressTimer = setInterval(pollScanProgress, 300);
  
  try {
    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("files", file, file.name));
    
    await request("/admin/import-directory", {
      method: "POST",
      body: formData,
    });
    
    const finalProgress = await request("/admin/scan-progress");
    const elapsed = finalProgress.start_time ? Math.floor((Date.now() / 1000) - finalProgress.start_time) : 0;
    const elapsedStr = elapsed < 60 ? `${elapsed}秒` : `${Math.floor(elapsed / 60)}分${elapsed % 60}秒`;
    
    for (let i = 0; i < 5; i++) {
      await pollScanProgress();
      await new Promise(r => setTimeout(r, 200));
    }
    
    els.scanProgressWrap.classList.add("hidden");
    els.scanSummary.classList.remove("hidden");
    els.scanSummary.textContent = `添加完成，总共${finalProgress.total_count}个文件，新增${finalProgress.added_count}个文件，跳过${finalProgress.skipped_count}个文件，总耗时${elapsedStr}`;
    await Promise.all([loadFilterOptions(), loadSongs()]);
    showToast("添加完成", "success");
    if (
      finalProgress.skipped_count > 0 &&
      Array.isArray(finalProgress.skipped_details) &&
      finalProgress.skipped_details.length
    ) {
      showSkippedFilesModal(finalProgress.skipped_details);
    }
  } catch (err) {
    showToast(`添加歌曲失败: ${err.message}`, "error");
  } finally {
    if (state.scanProgressTimer) {
      clearInterval(state.scanProgressTimer);
      state.scanProgressTimer = null;
    }
    els.addSongsBtn.disabled = false;
    els.addSongsBtn.textContent = "添加歌曲";
    els.songFilePicker.value = "";
    els.scanProgressWrap.classList.add("hidden");
    els.scanSummary.classList.remove("hidden");
  }
}

async function pollScanProgress() {
  try {
    const progress = await request("/admin/scan-progress");
    console.log("Scan progress:", progress);
    
    if (!progress.is_scanning && progress.scanned_count === 0 && progress.total_count === 0) {
      return;
    }
    
    const percent = progress.total_count > 0 ? Math.round((progress.scanned_count / progress.total_count) * 100) : 0;
    els.scanProgressFill.style.width = percent + "%";
    els.scanProgressText.textContent = progress.is_scanning ? "正在扫描..." : "扫描完成";
    els.scanProgressStats.textContent = `${progress.scanned_count} / ${progress.total_count} (${percent}%) - 新增: ${progress.added_count} 跳过: ${progress.skipped_count}`;
    
    console.log("start_time from backend:", progress.start_time, "current time:", Date.now());
    
    if (progress.start_time && progress.start_time > 0) {
      const elapsed = Math.floor((Date.now() / 1000) - progress.start_time);
      console.log("elapsed seconds:", elapsed);
      const elapsedStr = elapsed < 60 ? `${elapsed}秒` : `${Math.floor(elapsed / 60)}分${elapsed % 60}秒`;
      els.scanElapsedTime.textContent = `已耗时: ${elapsedStr}`;
      
      if (progress.scanned_count > 0 && progress.is_scanning) {
        const avgTime = elapsed / progress.scanned_count;
        const remaining = Math.round((progress.total_count - progress.scanned_count) * avgTime);
        const remainingStr = remaining < 60 ? `${remaining}秒` : `${Math.floor(remaining / 60)}分${remaining % 60}秒`;
        els.scanEstimatedTime.textContent = `预计剩余: ${remainingStr}`;
      }
    } else {
      els.scanElapsedTime.textContent = "已耗时: 0秒";
      els.scanEstimatedTime.textContent = "预计剩余: --";
    }
    
    if (!progress.is_scanning && state.scanProgressTimer) {
      clearInterval(state.scanProgressTimer);
      state.scanProgressTimer = null;
    }
  } catch (err) {
    console.error("Failed to poll scan progress:", err);
  }
}

/**
 * @param {number} songId
 * @param {number|null} currentFileId
 * @param {{ preserveMetadata?: boolean }} [options] preserveMetadata：为 true 时不覆盖抽屉内表单（仅刷新文件列表），用于添加/重命名/删除音频后保留未保存的编辑
 */
async function openEditModal(songId, currentFileId = null, options = {}) {
  const preserveMetadata = options.preserveMetadata === true;
  state.editingSongId = songId;
  state.editingCurrentFileId = currentFileId ?? null;
  const detail = await request(`/songs/${songId}`);
  if (!preserveMetadata) {
    els.titleInput.value = detail.title || "";
    renderArtistMultiSelect(els.leadArtistInput, detail.lead_artist_ids || [], "歌手");
    renderArtistMultiSelect(els.lyricistInput, detail.lyricist_ids || [], "作词");
    renderArtistMultiSelect(els.composerInput, detail.composer_ids || [], "作曲");
    els.albumInput.value = detail.album || "";
    if (els.filmTvInput) els.filmTvInput.value = detail.film_tv || "";
    const ms = detail.duration_ms;
    if (els.durationDisplay) els.durationDisplay.value = formatDurationForEdit(ms);
    syncReleaseDateField(detail.release_date || "");
    if (els.editLyricName) {
      const lrc = (detail.files || []).find((f) => /\.lrc$/i.test(f.original_filename || ""));
      els.editLyricName.textContent = lrc
        ? lrc.original_filename
        : (detail.lyricists || []).length
          ? "已录入作词信息"
          : "未关联 .lrc 文件";
    }
    if (els.languageInput) {
      let langIds = Array.isArray(detail.language_ids) && detail.language_ids.length ? [...detail.language_ids] : [];
      if (!langIds.length && detail.language && (state.languages || []).length) {
        langIds = detail.language.split(/,\s*/).map((n) => (state.languages || []).find((l) => l.name === n.trim())?.id).filter(Boolean);
      }
      renderLanguageMultiSelect(langIds);
    }
    const genreIds = (detail.genre_ids && detail.genre_ids.length) ? detail.genre_ids : detail.genre_id ? [detail.genre_id] : [];
    if (els.genreInput) renderGenreMultiSelect(genreIds);
    const selectedTagIds = (detail.tags || []).length
      ? state.tags.filter((tag) => detail.tags.includes(tag.name)).map((tag) => tag.id)
      : [];
    renderTagMultiSelect(selectedTagIds);
  }
  renderEditFormatsReadonly(detail.files || []);
  const fileCount = (detail.files || []).length;
  const isMultiFile = fileCount > 1;
  els.variantList.innerHTML = (detail.files || []).map((file) => {
    const isCurrentRow = currentFileId != null && file.id === currentFileId;
    const label = isCurrentRow && isMultiFile ? ' <span class="variant-current-label">当前列表行</span>' : "";
    const fmt = (file.format || "").toUpperCase();
    const metaLine = `${fmt} · ${file.bitrate ? `${file.bitrate} kbps` : "-"} · ${file.sample_rate ? `${file.sample_rate} Hz` : "-"} · ${formatSize(file.file_size)}`;
    return `<article class="variant-item${isCurrentRow ? " variant-item-current" : ""}" data-file-id="${file.id}">
      <div class="variant-row">
        <div class="variant-row-info">
          <strong class="variant-file-title">${escapeHtml(file.original_filename)}</strong>${label}
          <span class="variant-meta-inline">${escapeHtml(metaLine)}</span>
        </div>
        <div class="variant-row-actions">
          ${file.is_playable_web ? `<button type="button" class="icon-btn" data-variant-file-action="preview" data-file-id="${file.id}" data-format="${escapeHtml(file.format || "")}" title="试听" aria-label="试听">${VARIANT_ICONS.play}</button>` : ""}
          <button type="button" class="icon-btn" data-variant-file-action="download" data-file-id="${file.id}" title="下载" aria-label="下载">${VARIANT_ICONS.download}</button>
          <button type="button" class="icon-btn" data-variant-file-action="rename" data-file-id="${file.id}" data-file-format="${escapeHtml(file.format || "")}" title="重命名主文件名（扩展名不可改）" aria-label="重命名">${VARIANT_ICONS.rename}</button>
          <button type="button" class="icon-btn icon-btn-danger" data-variant-file-action="delete" data-file-id="${file.id}" title="删除（同时移除存储中的文件）" aria-label="删除">${VARIANT_ICONS.delete}</button>
        </div>
      </div>
    </article>`;
  }).join("");
  setupVariantListFileActions();
  let caption = document.getElementById("variantListHeading");
  if (!caption) {
    caption = document.createElement("p");
    caption.id = "variantListHeading";
    caption.className = "song-meta variant-list-caption";
    els.variantList.parentNode.insertBefore(caption, els.variantList);
  }
  if (fileCount > 0) {
    if (isMultiFile) {
      caption.textContent =
        currentFileId != null
          ? "多条音频：已标注当前列表行。右侧图标悬停可查看说明；支持重命名与添加文件。"
          : "多条音频共用一套元数据。图标悬停查看功能；列表「格式」用于播放。";
    } else {
      caption.textContent = "图标悬停可查看试听、下载、重命名、删除说明；可用「添加文件」增加格式版本。";
    }
    caption.style.display = "";
  } else {
    caption.textContent = "暂无音频文件，点击「添加文件」从本地上传。";
    caption.style.display = "";
  }
  openEditPanel();
  if (els.editOverlay) {
    els.editOverlay.classList.add("hidden");
    els.editOverlay.setAttribute("aria-hidden", "true");
  }
}

function closeEditModal() {
  closeEditPanel();
  if (els.editOverlay) {
    els.editOverlay.classList.add("hidden");
    els.editOverlay.setAttribute("aria-hidden", "true");
  }
  state.editingSongId = null;
  state.activeSongId = null;
  document.querySelectorAll(".adm-songs-table tbody tr.is-active").forEach((r) => r.classList.remove("is-active"));
  renderSongs();
  state.editingCurrentFileId = null;
}

async function saveSingleMetadata(event) {
  event.preventDefault();
  if (!state.editingSongId) return;
  const durationRaw = (els.durationDisplay?.value ?? "").trim();
  const durationParsed = parseDurationMmSs(durationRaw);
  if (!durationParsed.ok) {
    showToast("时长格式应为 mm:ss，例如 03:45", "error");
    return;
  }
  const languageIds = getSelectedLanguageIds();
  const leadIds = getSelectedArtistIds(els.leadArtistInput);
  const lyricIds = getSelectedArtistIds(els.lyricistInput);
  const composerIds = getSelectedArtistIds(els.composerInput);
  const genreIds = getSelectedGenreIds();
  await request(`/songs/${state.editingSongId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: els.titleInput.value.trim(),
      lead_artist_ids: leadIds,
      lyricist_ids: lyricIds,
      composer_ids: composerIds,
      album: els.albumInput.value.trim(),
      film_tv: (els.filmTvInput?.value ?? "").trim(),
      duration_ms: durationParsed.ms,
      language_ids: languageIds,
      genre_ids: genreIds,
      release_date: releaseDateFromForm(),
      tag_ids: getSelectedTagIds(),
    }),
  });
  recordMetadataArtistRecent(leadIds, lyricIds, composerIds);
  recordMetadataLanguageGenreRecent(languageIds, genreIds);
  closeEditModal();
  await loadSongs();
  showToast("歌曲元数据已更新", "success");
}

function getSelectedIds(selectEl) {
  return Array.from(selectEl.selectedOptions).map((option) => Number(option.value));
}

wireSearchFieldClear(
  els.keywordInput,
  els.keywordClearBtn,
  () => {
    state.songPage = 1;
    loadSongs().catch((err) => showToast(`查询失败: ${err.message}`, "error"));
  },
  () => updateAdminMusicResetVisibility()
);
wireSearchFieldClear(els.peopleSearchInput, els.peopleSearchClearBtn, () => renderPeopleManager());
wireSearchFieldClear(els.tagSearchInput, els.tagSearchClearBtn, () => renderTagManager());
wireSearchFieldClear(els.languageSearchInput, els.languageSearchClearBtn, () => renderLanguageManager());
wireSearchFieldClear(els.genreSearchInput, els.genreSearchClearBtn, () => renderGenreManager());

els.keywordInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    state.songPage = 1;
    loadSongs().catch((err) => showToast(`查询失败: ${err.message}`, "error"));
  }
});
els.resetSongFiltersBtn?.addEventListener("click", () => resetAdminSongListFilters());
function setAdminFiltersPanelOpen(open) {
  if (!els.admFiltersPanel || !els.toggleFilterBtn) return;
  els.admFiltersPanel.classList.toggle("hidden", !open);
  els.admFiltersPanel.setAttribute("aria-hidden", open ? "false" : "true");
  els.toggleFilterBtn.setAttribute("aria-expanded", open ? "true" : "false");
  els.toggleFilterBtn.textContent = open ? "收起筛选" : "更多筛选";
}

els.toggleFilterBtn?.addEventListener("click", () => {
  const willOpen = els.admFiltersPanel?.classList.contains("hidden");
  setAdminFiltersPanelOpen(willOpen);
});
els.sortButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const field = button.dataset.sort;
    if (state.sortBy === field) state.sortOrder = state.sortOrder === "asc" ? "desc" : "asc";
    else {
      state.sortBy = field;
      state.sortOrder = "asc";
    }
    state.songPage = 1;
    loadSongs().catch((err) => showToast(`排序失败: ${err.message}`, "error"));
  });
});
els.durationDisplay?.addEventListener("blur", () => {
  if (!els.durationDisplay) return;
  const v = els.durationDisplay.value.trim();
  if (!v) return;
  const normalized = normalizeDurationMmSs(v);
  if (normalized !== v) els.durationDisplay.value = normalized;
});
els.metadataForm.addEventListener("submit", (event) => saveSingleMetadata(event).catch((err) => showToast(`保存失败: ${err.message}`, "error")));
els.metadataForm?.addEventListener("click", (e) => {
  if (activeMultiSelect && !e.target.closest('.multi-select')) {
    activeMultiSelect.classList.add('hidden');
    activeMultiSelect = null;
  }
});
els.editCloseBtn?.addEventListener("click", closeEditModal);
els.editCancelBtn?.addEventListener("click", closeEditModal);
els.editDrawerBackdrop?.addEventListener("click", () => closeEditModal());
els.songAddFileBtn?.addEventListener("click", () => els.songAddFileInput?.click());
els.songAddFileInput?.addEventListener("change", async () => {
  const file = els.songAddFileInput?.files?.[0];
  if (els.songAddFileInput) els.songAddFileInput.value = "";
  if (!file || !state.editingSongId) return;
  const fd = new FormData();
  fd.append("file", file);
  try {
    const res = await fetch(`/songs/${state.editingSongId}/files`, { method: "POST", body: fd });
    if (!res.ok) {
      const msg = await parseResponseError(res);
      throw new Error(msg);
    }
    await res.json();
    showToast("文件已添加", "success");
    await openEditModal(state.editingSongId, state.editingCurrentFileId, { preserveMetadata: true });
    await loadSongs().catch(() => {});
  } catch (err) {
    const reason = err && err.message ? err.message : String(err);
    showToast(`添加文件失败：${reason}`, "error", reason.length > 120 ? 14000 : 9000);
  }
});
els.scanBtn.addEventListener("click", () => {
  els.directoryPicker.click();
});
els.addSongsBtn?.addEventListener("click", () => {
  els.songFilePicker.click();
});
els.songFilePicker.addEventListener("change", () => {
  addSongs().catch((err) => showToast(`添加歌曲失败: ${err.message}`, "error"));
});
els.selectAllSongs?.addEventListener("change", () => {
  const checked = els.selectAllSongs.checked;
  (state.songs || []).forEach((song) => {
    if (checked) state.selectedSongs.add(song.id);
    else state.selectedSongs.delete(song.id);
  });
  document.querySelectorAll(".song-checkbox").forEach((cb) => {
    cb.checked = checked;
  });
  updateBatchButtons();
});
els.batchMergeDuplicatesBtn?.addEventListener("click", () => batchMergeDuplicateSongs());
els.batchMergeSelectedBtn?.addEventListener("click", () => batchMergeSelectedSongs());
els.relocateSelectedStorageBtn?.addEventListener("click", () => relocateSelectedSongStorage());
els.batchDeleteBtn?.addEventListener("click", () => batchDeleteSongs());
els.batchDownloadBtn?.addEventListener("click", () => batchDownloadSongs());
els.directoryPicker.addEventListener("change", () => {
  runScan().catch((err) => showToast(`扫描失败: ${err.message}`, "error"));
});
els.adminNavMusic?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("music"); });
els.adminNavPeople?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("people"); loadPeople(); });
els.adminNavTags?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("tags"); loadTags(); });
els.adminNavLanguage?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("language"); loadLanguages(); });
function setAdminUserMenuOpen(open) {
  if (!els.adminUserMenu || !els.adminUserAvatarBtn) return;
  els.adminUserMenu.classList.toggle("hidden", !open);
  els.adminUserAvatarBtn.setAttribute("aria-expanded", open ? "true" : "false");
}

els.adminUserAvatarBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  const willOpen = els.adminUserMenu?.classList.contains("hidden");
  setAdminUserMenuOpen(willOpen);
});

els.goFrontendBtn?.addEventListener("click", () => {
  setAdminUserMenuOpen(false);
  window.location.href = "/";
});
els.tagSearchInput?.addEventListener("input", renderTagManager);
els.tagNewBtn?.addEventListener("click", () => openCreateModal("tag"));
els.peopleSearchInput?.addEventListener("input", renderPeopleManager);
els.peopleNewBtn?.addEventListener("click", () => openCreateModal("person"));
els.languageSearchInput?.addEventListener("input", renderLanguageManager);
els.languageNewBtn?.addEventListener("click", () => openCreateModal("language"));
els.genreSearchInput?.addEventListener("input", renderGenreManager);
els.genreNewBtn?.addEventListener("click", () => openCreateModal("genre"));

function bindManagerSelectAll(manager, selectAllEl, tableBodyEl, setKey) {
  if (!selectAllEl || !tableBodyEl) return;
  selectAllEl.addEventListener("change", () => {
    const checkboxes = tableBodyEl.querySelectorAll(".manager-row-checkbox");
    const checked = selectAllEl.checked;
    checkboxes.forEach((cb) => {
      cb.checked = checked;
      const id = parseInt(cb.dataset.id);
      if (checked) state[setKey].add(id); else state[setKey].delete(id);
    });
    updateManagerBatchButton(manager);
  });
}

function openBatchDeleteModal(manager) {
  const set = state[manager === "people" ? "selectedPeople" : manager === "tag" ? "selectedTags" : manager === "language" ? "selectedLanguages" : "selectedGenres"];
  const label = manager === "people" ? "艺人" : manager === "tag" ? "标签" : manager === "language" ? "语言" : "风格";
  state.batchDeleteIds = Array.from(set);
  state.batchDeleteManager = manager;
  state.deleteModalType = null;
  state.deleteModalId = null;
  els.deleteMessage.textContent = `确认删除选中的 ${state.batchDeleteIds.length} 个${label}吗？`;
  els.deleteOverlay.classList.remove("hidden");
}

bindManagerSelectAll("people", els.selectAllPeople, els.peopleTableBody, "selectedPeople");
bindManagerSelectAll("tag", els.selectAllTags, els.tagTableBody, "selectedTags");
bindManagerSelectAll("language", els.selectAllLanguages, els.languageTableBody, "selectedLanguages");
bindManagerSelectAll("genre", els.selectAllGenres, els.genreTableBody, "selectedGenres");
els.peopleBatchDeleteBtn?.addEventListener("click", () => openBatchDeleteModal("people"));
els.tagBatchDeleteBtn?.addEventListener("click", () => openBatchDeleteModal("tag"));
els.languageBatchDeleteBtn?.addEventListener("click", () => openBatchDeleteModal("language"));
els.genreBatchDeleteBtn?.addEventListener("click", () => openBatchDeleteModal("genre"));

document.addEventListener("click", (e) => {
  const btn = e.target.closest(".manager-sort-btn");
  if (!btn) return;
  e.preventDefault();
  const manager = btn.dataset.manager;
  const field = btn.dataset.sort;
  if (!manager || !field) return;
  const sortByKey = `${manager}SortBy`;
  const sortOrderKey = `${manager}SortOrder`;
  if (state[sortByKey] === field) {
    state[sortOrderKey] = state[sortOrderKey] === "asc" ? "desc" : "asc";
  } else {
    state[sortByKey] = field;
    state[sortOrderKey] = "asc";
  }
  if (manager === "people") renderPeopleManager();
  else if (manager === "tag") renderTagManager();
  else if (manager === "language") renderLanguageManager();
  else if (manager === "genre") renderGenreManager();
  updateManagerSortIndicators(manager);
});
els.createForm?.addEventListener("submit", submitCreateForm);
els.createCloseBtn?.addEventListener("click", closeCreateModal);
els.createCancelBtn?.addEventListener("click", closeCreateModal);
els.createOverlay?.addEventListener("click", (e) => { if (e.target === els.createOverlay) closeCreateModal(); });
els.itemEditForm?.addEventListener("submit", submitEditForm);
els.itemEditCloseBtn?.addEventListener("click", closeItemEditModal);
els.itemEditCancelBtn?.addEventListener("click", closeItemEditModal);
els.itemEditOverlay?.addEventListener("click", (e) => { 
  e.stopPropagation();
  if (e.target === els.itemEditOverlay) closeItemEditModal(); 
});
els.deleteCloseBtn?.addEventListener("click", closeDeleteModal);
els.deleteCancelBtn?.addEventListener("click", closeDeleteModal);
els.deleteConfirmBtn?.addEventListener("click", confirmDelete);
els.deleteOverlay?.addEventListener("click", (e) => { 
  e.stopPropagation();
  if (e.target === els.deleteOverlay) closeDeleteModal(); 
});
els.skippedCloseBtn?.addEventListener("click", closeSkippedFilesModal);
els.skippedDismissBtn?.addEventListener("click", closeSkippedFilesModal);
els.skippedOverlay?.addEventListener("click", (e) => {
  if (e.target === els.skippedOverlay) closeSkippedFilesModal();
});
els.modalCancelBtn.addEventListener("click", () => closeModal(null));
els.modalConfirmBtn.addEventListener("click", () => closeModal(els.modalInputWrap.classList.contains("hidden") ? true : els.modalInput.value));
els.modalOverlay.addEventListener("click", (event) => { 
  event.stopPropagation();
  if (event.target === els.modalOverlay) closeModal(null); 
});
els.modalInput.addEventListener("keydown", (event) => { if (event.key === "Enter") closeModal(els.modalInput.value); });
document.addEventListener("click", (e) => {
  if (els.adminUserMenu && !els.adminUserMenu.classList.contains("hidden")) {
    const inUserMenu = els.adminUserMenu.contains(e.target);
    const onAvatar = els.adminUserAvatarBtn?.contains(e.target);
    if (!inUserMenu && !onAvatar) setAdminUserMenuOpen(false);
  }
  document.querySelectorAll('.table-more-menu').forEach((node) => {
    node.classList.add("hidden");
    node.classList.remove("table-more-menu-fixed");
    node.style.top = "";
    node.style.left = "";
    node.style.right = "";
    const home = node._tableMoreHome;
    if (home && node.parentNode === document.body) home.appendChild(node);
  });
  if (activeMultiSelect) {
    activeMultiSelect.classList.add('hidden');
    activeMultiSelect = null;
  }
  closeActiveSearchableSelectMenuOnOutsideClick(e.target);
});

function preferredFormatForQueueItem(item) {
  if (!item || item.id == null) return "";
  return state.songFormatPreference[item.id] || "";
}

els.adminPrevBtn?.addEventListener("click", () => {
  playAdminAdjacentSong(-1).catch((err) => showToast(`播放失败: ${err.message || err}`, "error"));
});
els.adminNextBtn?.addEventListener("click", () => {
  playAdminAdjacentSong(1).catch((err) => showToast(`播放失败: ${err.message || err}`, "error"));
});
els.adminPlayModeSelect?.addEventListener("change", (event) => {
  state.playMode = event.target.value;
  syncAdminTransportDecorations();
});
els.adminAudioPlayer?.addEventListener("ended", () => {
  if (state.playMode === "single-loop" && state.currentPlayIndex >= 0 && state.playQueue[state.currentPlayIndex]) {
    const item = state.playQueue[state.currentPlayIndex];
    playSongInAdmin(item.id, preferredFormatForQueueItem(item), state.currentPlayIndex).catch(() => {});
    return;
  }
  playAdminAdjacentSong(1).catch(() => {});
});

els.pagePrevBtn?.addEventListener("click", () => {
  if (state.songPage > 1) {
    state.songPage -= 1;
    loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
  }
});
els.pageNextBtn?.addEventListener("click", () => {
  const totalPages = Math.max(1, Math.ceil(state.songListTotal / state.songPageSize));
  if (state.songPage < totalPages) {
    state.songPage += 1;
    loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
  }
});
els.pageSizeSelect?.addEventListener("change", () => {
  state.songPageSize = Number(els.pageSizeSelect.value) || 20;
  state.songPage = 1;
  loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
});
const onQuickFilterChange = () => {
  syncQuickFiltersFromUi();
  state.songPage = 1;
  loadSongs().catch((err) => showToast(`加载失败: ${err.message}`, "error"));
  updateAdminMusicResetVisibility();
};
ADMIN_QUICK_FILTER_SELECTS().forEach((el) => {
  el?.addEventListener("change", onQuickFilterChange);
});
initAdminMusicQuickFilters();
els.logoutBtn?.addEventListener("click", () => {
  setAdminUserMenuOpen(false);
  showToast("已退出（演示：刷新页面可重新进入）", "info");
});
els.editLyricReplaceBtn?.addEventListener("click", () => {
  if (!state.editingSongId) {
    showToast("请先选择一首歌曲", "info");
    return;
  }
  els.editLyricFileInput?.click();
});
els.editLyricFileInput?.addEventListener("change", async (e) => {
  const file = e.target.files?.[0];
  e.target.value = "";
  if (!file || !state.editingSongId) return;
  if (!/\.lrc$/i.test(file.name || "")) {
    showToast("请选择 .lrc 歌词文件", "error");
    return;
  }
  try {
    const result = await uploadLyricForSong(state.editingSongId, file);
    if (els.editLyricName) {
      els.editLyricName.textContent = result?.filename || file.name;
    }
    if (state.lyricSongId === state.editingSongId) {
      state.lyricLines = result?.lines || [];
      state.lyricContent = result?.content || "";
    }
    showToast("歌词已上传", "success");
  } catch (err) {
    showToast(`歌词上传失败: ${err.message || err}`, "error");
  }
});
document.querySelectorAll("[data-nav-placeholder]").forEach((btn) => {
  btn.addEventListener("click", () => showToast(`${btn.textContent?.trim() || "该功能"}即将推出`, "info"));
});
document.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    els.keywordInput?.focus();
  }
});
if (els.admFiltersPanel?.classList.contains("hidden")) {
  setAdminFiltersPanelOpen(false);
}

const ADMIN_SIDEBAR_COLLAPSED_KEY = "pm.sidebarCollapsed.admin";

function readAdminSidebarCollapsedPref() {
  try {
    return localStorage.getItem(ADMIN_SIDEBAR_COLLAPSED_KEY) === "1";
  } catch {
    return false;
  }
}

function writeAdminSidebarCollapsedPref(collapsed) {
  try {
    localStorage.setItem(ADMIN_SIDEBAR_COLLAPSED_KEY, collapsed ? "1" : "0");
  } catch {
    /* ignore storage failures */
  }
}

function setAdminSidebarCollapsed(collapsed) {
  const shell = document.querySelector(".admin-app .app-shell");
  const btn = document.querySelector("#adminSidebarCollapseBtn");
  if (!shell || !btn) return;
  shell.classList.toggle("is-sidebar-collapsed", collapsed);
  btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
  btn.setAttribute("aria-label", collapsed ? "展开侧栏" : "收起侧栏");
}

function initAdminSidebarCollapse() {
  const shell = document.querySelector(".admin-app .app-shell");
  const btn = document.querySelector("#adminSidebarCollapseBtn");
  if (!shell || !btn || btn.dataset.admSidebarCollapseBound === "1") return;
  btn.dataset.admSidebarCollapseBound = "1";
  setAdminSidebarCollapsed(readAdminSidebarCollapsedPref());
  btn.addEventListener("click", () => {
    const collapsed = !shell.classList.contains("is-sidebar-collapsed");
    setAdminSidebarCollapsed(collapsed);
    writeAdminSidebarCollapsedPref(collapsed);
  });
}

applyAppVersion();
initAdminSidebarCollapse();
initAdminStudioPlayer();

Promise.all([
  loadTags(),
  loadLanguages(),
  loadGenres(),
  loadPeople(),
  loadFilterOptions(),
  loadSongs(),
]).then(() => {
  populateQuickFilterOptions();
  updateAdminStats();
}).catch((err) => {
  showToast("加载失败: " + (err && err.message ? err.message : String(err)), "error");
});
