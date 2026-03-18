const state = {
  songs: [],
  tags: [],
  languages: [],
  genres: [],
  people: [],
  filters: null,
  editingSongId: null,
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
};

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
  adminNavGenre: document.querySelector("#adminNavGenre"),
  genreSearchInput: document.querySelector("#genreSearchInput"),
  genreNewBtn: document.querySelector("#genreNewBtn"),
  genreManagerList: document.querySelector("#genreManagerList"),
  goFrontendBtn: document.querySelector("#goFrontendBtn"),
  keywordInput: document.querySelector("#keywordInput"),
  toggleFilterBtn: document.querySelector("#toggleFilterBtn"),
  filterSection: document.querySelector("#filterSection"),
  formatFilter: document.querySelector("#formatFilter"),
  leadArtistFilter: document.querySelector("#leadArtistFilter"),
  tagFilter: document.querySelector("#tagFilter"),
  languageFilter: document.querySelector("#languageFilter"),
  genreFilter: document.querySelector("#genreFilter"),
  genreInput: document.querySelector("#genreInput"),
  lyricistFilter: document.querySelector("#lyricistFilter"),
  composerFilter: document.querySelector("#composerFilter"),
  scanSummary: document.querySelector("#scanSummary"),
  songTableBody: document.querySelector("#songTableBody"),
  sortButtons: Array.from(document.querySelectorAll(".sort-btn")),
  selectAllSongs: document.querySelector("#selectAllSongs"),
  batchDeleteBtn: document.querySelector("#batchDeleteBtn"),
  batchDownloadBtn: document.querySelector("#batchDownloadBtn"),
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
  metadataForm: document.querySelector("#metadataForm"),
  titleInput: document.querySelector("#titleInput"),
  leadArtistInput: document.querySelector("#leadArtistInput"),
  lyricistInput: document.querySelector("#lyricistInput"),
  composerInput: document.querySelector("#composerInput"),
  albumInput: document.querySelector("#albumInput"),
  durationInput: document.querySelector("#durationInput"),
  languageInput: document.querySelector("#languageInput"),
  releaseDateInput: document.querySelector("#releaseDateInput"),
  singleTagOptions: document.querySelector("#singleTagOptions"),
  variantList: document.querySelector("#variantList"),
  editCloseBtn: document.querySelector("#editCloseBtn"),
  editCancelBtn: document.querySelector("#editCancelBtn"),
  tagSearchInput: document.querySelector("#tagSearchInput"),
  tagNewBtn: document.querySelector("#tagNewBtn"),
  tagManagerList: document.querySelector("#tagManagerList"),
  tagTableBody: document.querySelector("#tagTableBody"),
  peopleSearchInput: document.querySelector("#peopleSearchInput"),
  peopleNewBtn: document.querySelector("#peopleNewBtn"),
  peopleBatchDeleteBtn: document.querySelector("#peopleBatchDeleteBtn"),
  selectAllPeople: document.querySelector("#selectAllPeople"),
  peopleManagerList: document.querySelector("#peopleManagerList"),
  peopleTableBody: document.querySelector("#peopleTableBody"),
  languageSearchInput: document.querySelector("#languageSearchInput"),
  languageNewBtn: document.querySelector("#languageNewBtn"),
  languageBatchDeleteBtn: document.querySelector("#languageBatchDeleteBtn"),
  selectAllLanguages: document.querySelector("#selectAllLanguages"),
  languageManagerList: document.querySelector("#languageManagerList"),
  languageTableBody: document.querySelector("#languageTableBody"),
  genreSearchInput: document.querySelector("#genreSearchInput"),
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
  adminNowPlaying: document.querySelector("#adminNowPlaying"),
  adminPrevBtn: document.querySelector("#adminPrevBtn"),
  adminNextBtn: document.querySelector("#adminNextBtn"),
  adminPlayModeSelect: document.querySelector("#adminPlayModeSelect"),
  adminAudioPlayer: document.querySelector("#adminAudioPlayer"),
};

const modalState = { resolver: null };
let activeMultiSelect = null;

async function request(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  els.toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 2800);
}

function adminNextPlayIndex() {
  if (!state.playQueue.length) return -1;
  if (state.playMode === "single-loop") return state.currentPlayIndex;
  if (state.playMode === "shuffle") return Math.floor(Math.random() * state.playQueue.length);
  if (state.currentPlayIndex < state.playQueue.length - 1) return state.currentPlayIndex + 1;
  if (state.playMode === "list-loop") return 0;
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

async function playSongInAdmin(songId, preferredFormat = "") {
  const url = preferredFormat ? `/songs/${songId}/play?preferred_format=${encodeURIComponent(preferredFormat)}` : `/songs/${songId}/play`;
  const playInfo = await request(url);
  state.playQueue = state.songs.slice();
  state.currentPlayIndex = state.playQueue.findIndex((s) => s.id === songId);
  const song = state.playQueue[state.currentPlayIndex] || { title: "未知歌曲" };
  if (els.adminAudioPlayer) {
    els.adminAudioPlayer.src = playInfo.stream_url;
    await els.adminAudioPlayer.play();
  }
  if (els.adminNowPlaying) els.adminNowPlaying.textContent = `${song.title || "未知歌曲"} · ${(playInfo.selected_format || "").toUpperCase()}`;
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
  document.querySelectorAll(".admin-nav-item").forEach((el) => el.classList.remove("active"));
  const pageEl = document.getElementById(`admin-page-${page}`);
  const navEl = document.querySelector(`.admin-nav-item[data-page="${page}"]`);
  if (pageEl) pageEl.classList.remove("hidden");
  if (navEl) navEl.classList.add("active");
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
  if (!ms) return "00:00";
  const total = Math.floor(ms / 1000);
  return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}

function formatSize(bytes) {
  if (!bytes) return "-";
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
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

function renderSelectOptions(selectEl, values, formatter = (x) => x) {
  selectEl.innerHTML = [`<option value="">全部</option>`, ...values.map((value) => `<option value="${value}">${formatter(value)}</option>`)].join("");
}

function selectedTagIdsFromContainer(container) {
  return Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map((node) => Number(node.value));
}

function peopleByType(type) {
  return state.people.filter((person) => (person.types || []).includes(type));
}

function renderArtistMultiSelect(container, selectedIds = [], type = "歌手") {
  const sourcePeople = peopleByType(type);
  const validSelectedIds = selectedIds.filter((id) => sourcePeople.some((person) => person.id === id));
  const selectedNames = sourcePeople.filter((person) => validSelectedIds.includes(person.id)).map((person) => person.name);
  container.innerHTML = `
    <div class="multi-select-trigger" role="button" tabindex="0">${selectedNames.length ? `<span class="tag-list">${selectedNames.map((name) => `<span class="tag">${name}</span>`).join("")}</span>` : "请选择"}</div>
    <div class="multi-select-menu hidden">
      <input type="text" class="multi-select-search" placeholder="搜索..." />
      <div class="multi-select-options">
        ${sourcePeople.map((person) => `<div class="artist-option"><input type="checkbox" value="${person.id}" ${validSelectedIds.includes(person.id) ? "checked" : ""} /><span>${person.name}</span></div>`).join("")}
      </div>
    </div>
  `;
  const trigger = container.querySelector('.multi-select-trigger');
  const menu = container.querySelector('.multi-select-menu');
  const searchInput = menu.querySelector('.multi-select-search');
  trigger.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (activeMultiSelect && activeMultiSelect !== menu) {
      activeMultiSelect.classList.add('hidden');
    }
    const willOpen = menu.classList.contains('hidden');
    menu.classList.toggle('hidden', !willOpen);
    activeMultiSelect = willOpen ? menu : null;
    if (willOpen) setTimeout(() => searchInput?.focus(), 0);
  });
  menu.addEventListener('click', (event) => {
    event.stopPropagation();
  });
  searchInput?.addEventListener('input', (event) => {
    const keyword = event.target.value.toLowerCase();
    const options = menu.querySelectorAll('.artist-option');
    options.forEach((option) => {
      const text = option.querySelector('span').textContent.toLowerCase();
      option.style.display = keyword && !text.includes(keyword) ? 'none' : '';
    });
  });
  menu.addEventListener('change', (event) => {
    if (event.target.type === 'checkbox') {
      renderArtistMultiSelect(container, getSelectedArtistIds(container), type);
      const nextMenu = container.querySelector('.multi-select-menu');
      nextMenu?.classList.remove('hidden');
      activeMultiSelect = nextMenu || null;
    }
  });
}

function getSelectedArtistIds(container) {
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

function renderTagOptions(container, selectedIds = []) {
  container.innerHTML = "";
  if (!state.tags.length) {
    container.innerHTML = '<span class="song-meta">暂无标签</span>';
    return;
  }
  state.tags.forEach((tag) => {
    const label = document.createElement("label");
    label.className = "tag-option";
    label.innerHTML = `<input type="checkbox" value="${tag.id}" ${selectedIds.includes(tag.id) ? "checked" : ""} /><span>${tag.name}</span>`;
    container.appendChild(label);
  });
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
  const songs = state.songs || [];
  if (!songs.length) {
    els.songTableBody.innerHTML = '<tr><td colspan="15" class="empty-cell">暂无歌曲</td></tr>';
    renderSortIndicators();
    return;
  }
  
  const allSelected = songs.length > 0 && songs.every(s => state.selectedSongs.has(s.id));
  els.selectAllSongs.checked = allSelected;

  songs.forEach((song, index) => {
    const tr = document.createElement("tr");
    const isChecked = state.selectedSongs.has(song.id);
    tr.innerHTML = `
      <td><input type="checkbox" class="song-checkbox" value="${song.id}" ${isChecked ? "checked" : ""} /></td>
      <td>${index + 1}</td>
      <td><button class="song-link-btn" data-role="title" type="button">${song.title || "-"}</button></td>
      <td>${song.lead_artist || "-"}</td>
      <td>${(song.lyricists || []).join(" / ") || "-"}</td>
      <td>${(song.composers || []).join(" / ") || "-"}</td>
      <td>${song.album || "-"}</td>
      <td>${song.language || "-"}</td>
      <td>${song.genre || "-"}</td>
      <td>${(song.tags || []).join(" / ") || "-"}</td>
      <td>${song.release_date || "-"}</td>
      <td>${formatDuration(song.duration_ms)}</td>
      <td>${song.file_format ? song.file_format.toUpperCase() : "-"}</td>
      <td>${formatSize(song.file_size)}</td>
      <td>${formatDate(song.created_at)}</td>
      <td>
        <div class="table-more">
          <button class="btn table-more-btn" data-role="more" type="button" aria-label="更多">⋮</button>
          <div class="table-more-menu hidden" data-role="menu">
            <button class="btn menu-btn" data-role="preview" type="button">▶ 试听</button>
            <button class="btn menu-btn" data-role="download" type="button">↓ 下载</button>
            <button class="btn menu-btn" data-role="edit" type="button">✎ 编辑</button>
            <button class="btn menu-btn danger-text" data-role="delete" type="button">🗑 删除</button>
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
    tr.querySelector('[data-role="title"]').addEventListener("click", () => openEditModal(song.id));
    const moreBtn = tr.querySelector('[data-role="more"]');
    const menu = tr.querySelector('[data-role="menu"]');
    const tableMore = moreBtn.closest(".table-more");
    moreBtn.addEventListener("click", (event) => {
      event.stopPropagation();
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
    tr.querySelector('[data-role="preview"]')?.addEventListener("click", () => {
      closeMenuAndReturnHome();
      playSongInAdmin(song.id).catch((err) => showToast(`试听失败: ${err.message || err}`, "error"));
    });
    tr.querySelector('[data-role="download"]')?.addEventListener("click", async () => {
      closeMenuAndReturnHome();
      try {
        const playInfo = await request(`/songs/${song.id}/play`);
        const link = document.createElement("a");
        link.href = playInfo.download_url;
        link.download = "";
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (err) {
        showToast(`下载失败: ${err.message || err}`, "error");
      }
    });
    tr.querySelector('[data-role="edit"]').addEventListener("click", () => {
      closeMenuAndReturnHome();
      openEditModal(song.id);
    });
    tr.querySelector('[data-role="delete"]').addEventListener("click", async () => {
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
}

function updateBatchButtons() {
  const selectedCount = state.selectedSongs.size;
  if (selectedCount > 0) {
    els.batchDeleteBtn.classList.remove("hidden");
    els.batchDeleteBtn.textContent = `批量删除 (${selectedCount})`;
    els.batchDownloadBtn.classList.remove("hidden");
    els.batchDownloadBtn.textContent = `批量下载 (${selectedCount})`;
  } else {
    els.batchDeleteBtn.classList.add("hidden");
    els.batchDownloadBtn.classList.add("hidden");
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

async function batchDownloadSongs() {
  const ids = getSelectedSongIds();
  if (!ids.length) return;
  const idsParam = ids.join(",");
  window.location.href = `/admin/songs/batch-download?song_ids=${idsParam}`;
  showToast(`正在打包下载 ${ids.length} 首歌曲`, "success");
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
  const f = state.filters || {};
  if (els.formatFilter) renderSelectOptions(els.formatFilter, f.formats || [], (v) => v.toUpperCase());
  if (els.leadArtistFilter) renderSelectOptions(els.leadArtistFilter, f.lead_artists || []);
  if (els.tagFilter) els.tagFilter.innerHTML = ['<option value="">全部</option>', ...(f.tags || []).map((tag) => `<option value="${tag.id}">${tag.name}</option>`)].join("");
  if (els.languageFilter) els.languageFilter.innerHTML = ['<option value="">全部</option>', ...(f.languages || []).map((language) => `<option value="${language.name}">${language.name}</option>`)].join("");
  if (els.genreFilter) els.genreFilter.innerHTML = ['<option value="">全部</option>', ...(f.genres || []).map((genre) => `<option value="${genre.id}">${genre.name}</option>`)].join("");
  if (els.lyricistFilter) renderSelectOptions(els.lyricistFilter, f.lyricists || []);
  if (els.composerFilter) renderSelectOptions(els.composerFilter, f.composers || []);
}

async function loadTags() {
  try {
    state.tags = await request("/tags");
  } catch (err) {
    state.tags = [];
    showToast("加载标签失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  renderTagManager();
  updateManagerSortIndicators("tag");
}

async function loadLanguages() {
  try {
    state.languages = await request("/languages");
  } catch (err) {
    state.languages = [];
    showToast("加载语言失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  renderLanguageMultiSelect();
  renderLanguageManager();
  updateManagerSortIndicators("language");
}

function renderLanguageMultiSelect(selectedIds = []) {
  if (!els.languageInput) return;
  const options = state.languages || [];
  const validSelectedIds = selectedIds.filter((id) => options.some((lang) => lang.id === id));
  els.languageInput.innerHTML = `
    <div class="multi-select-trigger" role="button" tabindex="0">${validSelectedIds.length ? `<span class="tag-list">${options.filter((l) => validSelectedIds.includes(l.id)).map((l) => `<span class="tag">${l.name}</span>`).join("")}</span>` : "请选择语言"}</div>
    <div class="multi-select-menu hidden">
      <input type="text" class="multi-select-search" placeholder="搜索..." />
      <div class="multi-select-options">
        ${options.map((lang) => `<div class="artist-option"><input type="checkbox" value="${lang.id}" data-name="${lang.name}" ${validSelectedIds.includes(lang.id) ? "checked" : ""} /><span>${lang.name}</span></div>`).join("")}
      </div>
    </div>
  `;
  const trigger = els.languageInput.querySelector('.multi-select-trigger');
  const menu = els.languageInput.querySelector('.multi-select-menu');
  const searchInput = menu.querySelector('.multi-select-search');
  trigger.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (activeMultiSelect && activeMultiSelect !== menu) {
      activeMultiSelect.classList.add('hidden');
    }
    const willOpen = menu.classList.contains('hidden');
    menu.classList.toggle('hidden', !willOpen);
    activeMultiSelect = willOpen ? menu : null;
    if (willOpen) setTimeout(() => searchInput?.focus(), 0);
  });
  menu.addEventListener('click', (event) => {
    event.stopPropagation();
  });
  searchInput?.addEventListener('input', (event) => {
    const keyword = event.target.value.toLowerCase();
    const opts = menu.querySelectorAll('.artist-option');
    opts.forEach((option) => {
      const text = option.querySelector('span').textContent.toLowerCase();
      option.style.display = keyword && !text.includes(keyword) ? 'none' : '';
    });
  });
  menu.addEventListener('change', (event) => {
    if (event.target.type === 'checkbox') {
      updateLanguageTrigger();
    }
  });
}

function updateLanguageTrigger() {
  if (!els.languageInput) return;
  const checked = els.languageInput.querySelectorAll('input[type="checkbox"]:checked');
  const trigger = els.languageInput.querySelector('.multi-select-trigger');
  if (checked.length) {
    trigger.innerHTML = `<span class="tag-list">${Array.from(checked).map(cb => `<span class="tag">${cb.dataset.name}</span>`).join("")}</span>`;
  } else {
    trigger.textContent = "请选择语言";
  }
}

function getSelectedLanguageIds() {
  if (!els.languageInput) return [];
  return Array.from(els.languageInput.querySelectorAll('input[type="checkbox"]:checked')).map(cb => Number(cb.value));
}

async function loadGenres() {
  try {
    state.genres = await request("/genres");
  } catch (err) {
    state.genres = [];
    showToast("加载风格失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  if (els.genreInput) {
    els.genreInput.innerHTML = ['<option value="0">无</option>', ...state.genres.map((g) => `<option value="${g.id}">${g.name}</option>`)].join("");
  }
  renderGenreManager();
  updateManagerSortIndicators("genre");
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
}

async function loadSongs() {
  state.selectedSongs.clear();
  updateBatchButtons();
  try {
    const params = new URLSearchParams();
    if (els.keywordInput && els.keywordInput.value.trim()) params.set("keyword", els.keywordInput.value.trim());
    if (els.formatFilter && els.formatFilter.value) params.append("formats", els.formatFilter.value);
    if (els.leadArtistFilter && els.leadArtistFilter.value) params.append("lead_artists", els.leadArtistFilter.value);
    if (els.tagFilter && els.tagFilter.value) params.append("tag_ids", els.tagFilter.value);
    if (els.languageFilter && els.languageFilter.value) params.append("languages", els.languageFilter.value);
    if (els.genreFilter && els.genreFilter.value) params.append("genre_ids", els.genreFilter.value);
    if (els.lyricistFilter && els.lyricistFilter.value) params.append("lyricists", els.lyricistFilter.value);
    if (els.composerFilter && els.composerFilter.value) params.append("composers", els.composerFilter.value);
    params.set("sort_by", state.sortBy);
    params.set("sort_order", state.sortOrder);
    params.set("limit", "500");
    state.songs = await request(`/songs?${params.toString()}`);
  } catch (err) {
    state.songs = [];
    showToast("加载歌曲失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  renderSongs();
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

async function openEditModal(songId) {
  state.editingSongId = songId;
  const detail = await request(`/songs/${songId}`);
  els.titleInput.value = detail.title || "";
  renderArtistMultiSelect(els.leadArtistInput, detail.lead_artist_ids || [], "歌手");
  renderArtistMultiSelect(els.lyricistInput, detail.lyricist_ids || [], "作词");
  renderArtistMultiSelect(els.composerInput, detail.composer_ids || [], "作曲");
  els.albumInput.value = detail.album || "";
  els.durationInput.value = detail.duration_ms || "";
  els.releaseDateInput.value = detail.release_date || "";
  const selectedLanguage = state.languages.find((language) => language.name === detail.language);
  if (els.languageInput) {
    renderLanguageMultiSelect(selectedLanguage ? [selectedLanguage.id] : []);
  }
  if (els.genreInput) els.genreInput.value = String(detail.genre_id || 0);
  const selectedTagIds = state.tags.filter((tag) => detail.tags.includes(tag.name)).map((tag) => tag.id);
  renderTagOptions(els.singleTagOptions, selectedTagIds);
  els.variantList.innerHTML = detail.files.map((file) => `<article class="variant-item"><strong>${file.original_filename}</strong><p class="variant-meta">${file.format.toUpperCase()} · ${file.bitrate ? `${file.bitrate} kbps` : "-"} · ${file.sample_rate ? `${file.sample_rate} Hz` : "-"} · ${formatSize(file.file_size)}</p></article>`).join("");
  els.editOverlay.classList.remove("hidden");
}

function closeEditModal() {
  els.editOverlay.classList.add("hidden");
  state.editingSongId = null;
}

async function saveSingleMetadata(event) {
  event.preventDefault();
  if (!state.editingSongId) return;
  const genreId = els.genreInput ? Number(els.genreInput.value) : null;
  const languageIds = getSelectedLanguageIds();
  await request(`/songs/${state.editingSongId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: els.titleInput.value.trim(),
      lead_artist_ids: getSelectedArtistIds(els.leadArtistInput),
      lyricist_ids: getSelectedArtistIds(els.lyricistInput),
      composer_ids: getSelectedArtistIds(els.composerInput),
      album: els.albumInput.value.trim(),
      duration_ms: els.durationInput.value === "" ? null : Number(els.durationInput.value),
      language_id: languageIds.length > 0 ? languageIds[0] : null,
      genre_id: genreId === 0 ? null : genreId,
      release_date: els.releaseDateInput.value || null,
      tag_ids: selectedTagIdsFromContainer(els.singleTagOptions),
    }),
  });
  closeEditModal();
  await loadSongs();
  showToast("歌曲元数据已更新", "success");
}

function getSelectedIds(selectEl) {
  return Array.from(selectEl.selectedOptions).map((option) => Number(option.value));
}

els.keywordInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") loadSongs().catch((err) => showToast(`查询失败: ${err.message}`, "error"));
});
els.toggleFilterBtn.addEventListener("click", () => {
  els.filterSection.classList.toggle("hidden");
  els.toggleFilterBtn.textContent = els.filterSection.classList.contains("hidden") ? "展开筛选" : "收起筛选";
});
[els.formatFilter, els.leadArtistFilter, els.tagFilter, els.languageFilter, els.genreFilter, els.lyricistFilter, els.composerFilter].forEach((el) => {
  el.addEventListener("change", () => loadSongs().catch((err) => showToast(`筛选失败: ${err.message}`, "error")));
});
els.sortButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const field = button.dataset.sort;
    if (state.sortBy === field) state.sortOrder = state.sortOrder === "asc" ? "desc" : "asc";
    else {
      state.sortBy = field;
      state.sortOrder = "asc";
    }
    loadSongs().catch((err) => showToast(`排序失败: ${err.message}`, "error"));
  });
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
els.editOverlay?.addEventListener("click", (e) => { 
  e.stopPropagation();
  if (e.target === els.editOverlay) closeEditModal(); 
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
  state.selectedSongs.clear();
  if (checked) {
    state.songs.forEach(song => state.selectedSongs.add(song.id));
  }
  document.querySelectorAll('.song-checkbox').forEach(cb => cb.checked = checked);
  updateBatchButtons();
});
els.batchDeleteBtn?.addEventListener("click", () => batchDeleteSongs());
els.batchDownloadBtn?.addEventListener("click", () => batchDownloadSongs());
els.directoryPicker.addEventListener("change", () => {
  runScan().catch((err) => showToast(`扫描失败: ${err.message}`, "error"));
});
els.adminNavMusic?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("music"); });
els.adminNavPeople?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("people"); loadPeople(); });
els.adminNavTags?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("tags"); loadTags(); });
els.adminNavLanguage?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("language"); loadLanguages(); });
els.adminNavGenre?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("genre"); loadGenres(); });
els.goFrontendBtn?.addEventListener("click", () => { window.location.href = "/"; });
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
els.modalCancelBtn.addEventListener("click", () => closeModal(null));
els.modalConfirmBtn.addEventListener("click", () => closeModal(els.modalInputWrap.classList.contains("hidden") ? true : els.modalInput.value));
els.modalOverlay.addEventListener("click", (event) => { 
  event.stopPropagation();
  if (event.target === els.modalOverlay) closeModal(null); 
});
els.modalInput.addEventListener("keydown", (event) => { if (event.key === "Enter") closeModal(els.modalInput.value); });
document.addEventListener("click", () => {
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
});

els.adminPrevBtn?.addEventListener("click", () => {
  const idx = adminPrevPlayIndex();
  if (idx >= 0 && state.playQueue[idx]) playSongInAdmin(state.playQueue[idx].id).catch((err) => showToast(`播放失败: ${err.message || err}`, "error"));
});
els.adminNextBtn?.addEventListener("click", () => {
  const idx = adminNextPlayIndex();
  if (idx >= 0 && state.playQueue[idx]) playSongInAdmin(state.playQueue[idx].id).catch((err) => showToast(`播放失败: ${err.message || err}`, "error"));
});
els.adminPlayModeSelect?.addEventListener("change", (event) => { state.playMode = event.target.value; });
els.adminAudioPlayer?.addEventListener("ended", () => {
  const idx = adminNextPlayIndex();
  if (idx >= 0 && state.playQueue[idx]) playSongInAdmin(state.playQueue[idx].id).catch(() => {});
});

Promise.all([loadTags(), loadLanguages(), loadGenres(), loadPeople(), loadFilterOptions(), loadSongs()]).catch((err) => {
  showToast("加载失败: " + (err && err.message ? err.message : String(err)), "error");
});
