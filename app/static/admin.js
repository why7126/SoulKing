const state = {
  songs: [],
  tags: [],
  languages: [],
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
};

const els = {
  scanBtn: document.querySelector("#scanBtn"),
  directoryPicker: document.querySelector("#directoryPicker"),
  adminNavMusic: document.querySelector("#adminNavMusic"),
  adminNavPeople: document.querySelector("#adminNavPeople"),
  adminNavTags: document.querySelector("#adminNavTags"),
  adminNavLanguage: document.querySelector("#adminNavLanguage"),
  goFrontendBtn: document.querySelector("#goFrontendBtn"),
  keywordInput: document.querySelector("#keywordInput"),
  toggleFilterBtn: document.querySelector("#toggleFilterBtn"),
  filterSection: document.querySelector("#filterSection"),
  formatFilter: document.querySelector("#formatFilter"),
  leadArtistFilter: document.querySelector("#leadArtistFilter"),
  chorusArtistFilter: document.querySelector("#chorusArtistFilter"),
  tagFilter: document.querySelector("#tagFilter"),
  languageFilter: document.querySelector("#languageFilter"),
  lyricistFilter: document.querySelector("#lyricistFilter"),
  composerFilter: document.querySelector("#composerFilter"),
  scanSummary: document.querySelector("#scanSummary"),
  songTableBody: document.querySelector("#songTableBody"),
  sortButtons: Array.from(document.querySelectorAll(".sort-btn")),
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
  chorusArtistInput: document.querySelector("#chorusArtistInput"),
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
  peopleSearchInput: document.querySelector("#peopleSearchInput"),
  peopleNewBtn: document.querySelector("#peopleNewBtn"),
  peopleManagerList: document.querySelector("#peopleManagerList"),
  languageSearchInput: document.querySelector("#languageSearchInput"),
  languageNewBtn: document.querySelector("#languageNewBtn"),
  languageManagerList: document.querySelector("#languageManagerList"),
  createOverlay: document.querySelector("#createOverlay"),
  createModalTitle: document.querySelector("#createModalTitle"),
  createFormBody: document.querySelector("#createFormBody"),
  createForm: document.querySelector("#createForm"),
  createCloseBtn: document.querySelector("#createCloseBtn"),
  createCancelBtn: document.querySelector("#createCancelBtn"),
  createSubmitBtn: document.querySelector("#createSubmitBtn"),
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

function openCreateModal(type) {
  state.createModalType = type;
  const titleEl = els.createModalTitle;
  const bodyEl = els.createFormBody;
  if (!bodyEl || !titleEl) return;
  bodyEl.innerHTML = "";
  if (type === "tag") {
    titleEl.textContent = "新建标签";
    bodyEl.innerHTML = '<label class="form-field"><span>标签名称</span><input type="text" name="name" placeholder="输入新标签名称" /></label>';
  } else if (type === "language") {
    titleEl.textContent = "新建语言";
    bodyEl.innerHTML = '<label class="form-field"><span>语言名称</span><input type="text" name="name" placeholder="输入新语言名称" /></label>';
  } else if (type === "person") {
    titleEl.textContent = "新建艺人";
    bodyEl.innerHTML = `
      <label class="form-field"><span>艺人名称</span><input type="text" name="name" placeholder="输入艺人名称" /></label>
      <div class="form-field"><span>类型</span><div id="createPersonTypes" class="multi-select compact-multi-select"></div></div>
    `;
    const typesContainer = document.getElementById("createPersonTypes");
    if (typesContainer) renderTypeMultiSelect(typesContainer, ["歌手"]);
  }
  els.createOverlay.classList.remove("hidden");
}

function closeCreateModal() {
  state.createModalType = null;
  els.createOverlay.classList.add("hidden");
}

async function submitCreateForm(e) {
  e.preventDefault();
  const type = state.createModalType;
  if (!type) return;
  const bodyEl = els.createFormBody;
  const nameInput = bodyEl?.querySelector('input[name="name"]');
  const name = nameInput?.value?.trim() || "";
  if (!name) return;
  try {
    if (type === "tag") {
      await request("/tags", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
      await Promise.all([loadTags(), loadFilterOptions(), loadSongs()]);
      showToast("标签已创建", "success");
    } else if (type === "language") {
      await request("/languages", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
      await Promise.all([loadLanguages(), loadFilterOptions(), loadSongs()]);
      showToast("语言已创建", "success");
    } else if (type === "person") {
      const typesContainer = document.getElementById("createPersonTypes");
      const types = typesContainer ? (getSelectedTypes(typesContainer).length ? getSelectedTypes(typesContainer) : ["歌手"]) : ["歌手"];
      await request("/people", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, types }) });
      await Promise.all([loadPeople(), loadSongs()]);
      showToast("艺人已创建", "success");
    }
    closeCreateModal();
  } catch (err) {
    showToast("创建失败: " + (err && err.message ? err.message : String(err)), "error");
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
      ${sourcePeople.map((person) => `<div class="artist-option"><input type="checkbox" value="${person.id}" ${validSelectedIds.includes(person.id) ? "checked" : ""} /><span>${person.name}</span></div>`).join("")}
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
    menu.classList.toggle('hidden', !willOpen);
    activeMultiSelect = willOpen ? menu : null;
  });
  menu.addEventListener('click', (event) => {
    event.stopPropagation();
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
    els.songTableBody.innerHTML = '<tr><td colspan="14" class="empty-cell">暂无歌曲</td></tr>';
    renderSortIndicators();
    return;
  }

  songs.forEach((song) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><button class="song-link-btn" data-role="title" type="button">${song.title || "-"}</button></td>
      <td>${song.lead_artist || "-"}</td>
      <td>${song.chorus_artist || "-"}</td>
      <td>${(song.lyricists || []).join(" / ") || "-"}</td>
      <td>${(song.composers || []).join(" / ") || "-"}</td>
      <td>${song.album || "-"}</td>
      <td>${song.language || "-"}</td>
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
    tr.querySelector('[data-role="title"]').addEventListener("click", () => openEditModal(song.id));
    const moreBtn = tr.querySelector('[data-role="more"]');
    const menu = tr.querySelector('[data-role="menu"]');
    moreBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      document.querySelectorAll('.table-more-menu').forEach((node) => {
        if (node !== menu) node.classList.add("hidden");
      });
      menu.classList.toggle("hidden");
    });
    tr.querySelector('[data-role="preview"]')?.addEventListener("click", () => {
      menu.classList.add("hidden");
      playSongInAdmin(song.id).catch((err) => showToast(`试听失败: ${err.message || err}`, "error"));
    });
    tr.querySelector('[data-role="download"]')?.addEventListener("click", async () => {
      menu.classList.add("hidden");
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
    tr.querySelector('[data-role="edit"]').addEventListener("click", () => openEditModal(song.id));
    tr.querySelector('[data-role="delete"]').addEventListener("click", async () => {
      menu.classList.add("hidden");
      const ok = await openModal({ title: "删除歌曲", message: `确认删除歌曲「${song.title}」吗？`, confirmText: "删除", withInput: false });
      if (!ok) return;
      await request(`/songs/${song.id}`, { method: "DELETE" });
      await Promise.all([loadSongs(), loadFilterOptions()]);
      showToast("歌曲已删除", "success");
    });
    els.songTableBody.appendChild(tr);
  });

  renderSortIndicators();
}

function createInlineManagerItem(itemData, type) {
  const item = document.createElement("article");
  item.className = "tag-manager-item";
  item.innerHTML = `
    <div class="tag-manager-main">
      <strong class="tag-display">${itemData.name}</strong>
      ${type === "person" ? `<p class="song-meta tag-type-text">${(itemData.types || []).join(" / ") || "歌手"}</p>` : ""}
      <form class="tag-inline-edit hidden" data-role="edit-form">
        <input type="text" value="${itemData.name}" data-role="edit-input" />
        ${type === "person" ? '<div class="inline-edit-types" data-role="edit-types"></div>' : ''}
        <button class="btn btn-primary" type="submit">保存</button>
        <button class="btn" type="button" data-role="cancel-edit">取消</button>
      </form>
        <div class="tag-inline-delete hidden" data-role="delete-row">
          <span class="song-meta">确认删除该${type === "tag" ? "标签" : type === "language" ? "语言" : "艺人"}？</span>
        <button class="btn btn-primary danger-text" type="button" data-role="confirm-delete">删除</button>
        <button class="btn" type="button" data-role="cancel-delete">取消</button>
      </div>
    </div>
    <div class="variant-actions" data-role="actions">
      <button class="btn" data-role="rename">修改</button>
      <button class="btn danger-text" data-role="delete">删除</button>
    </div>
  `;

  const display = item.querySelector(".tag-display");
  const typeText = item.querySelector('.tag-type-text');
  const editForm = item.querySelector('[data-role="edit-form"]');
  const editInput = item.querySelector('[data-role="edit-input"]');
  const deleteRow = item.querySelector('[data-role="delete-row"]');
  const actions = item.querySelector('[data-role="actions"]');
  const editTypes = item.querySelector('[data-role="edit-types"]');
  if (type === 'person' && editTypes) {
    editForm.addEventListener('click', (e) => e.stopPropagation());
    renderTypeMultiSelect(editTypes, itemData.types || ["歌手"]);
  }

  item.querySelector('[data-role="rename"]').addEventListener("click", () => {
    actions.classList.add("hidden");
    deleteRow.classList.add("hidden");
    display.classList.add("hidden");
    if (typeText) typeText.classList.add('hidden');
    if (type === 'person' && editTypes) {
      renderTypeMultiSelect(editTypes, itemData.types || ["歌手"]);
    }
    editForm.classList.remove("hidden");
    editInput.focus();
    editInput.select();
  });

  item.querySelector('[data-role="cancel-edit"]').addEventListener("click", () => {
    editInput.value = itemData.name;
    editForm.classList.add("hidden");
    display.classList.remove("hidden");
    if (typeText) typeText.classList.remove('hidden');
    actions.classList.remove("hidden");
  });

  editForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = editInput.value.trim();
    if (!name) return;
    const path = type === "tag" ? `/tags/${itemData.id}` : type === "language" ? `/languages/${itemData.id}` : `/people/${itemData.id}`;
    const body = type === 'person' ? { name, types: getSelectedTypes(editTypes).length ? getSelectedTypes(editTypes) : ["歌手"] } : { name };
    await request(path, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (type === "tag") {
      await Promise.all([loadTags(), loadFilterOptions(), loadSongs()]);
      showToast("标签已更新", "success");
    } else if (type === "language") {
      await Promise.all([loadLanguages(), loadFilterOptions(), loadSongs()]);
      showToast("语言已更新", "success");
    } else {
      await Promise.all([loadPeople(), loadSongs()]);
      showToast("艺人已更新", "success");
    }
  });

  item.querySelector('[data-role="delete"]').addEventListener("click", () => {
    actions.classList.add("hidden");
    display.classList.add("hidden");
    if (typeText) typeText.classList.add('hidden');
    editForm.classList.add("hidden");
    deleteRow.classList.remove("hidden");
  });

  item.querySelector('[data-role="cancel-delete"]').addEventListener("click", () => {
    deleteRow.classList.add("hidden");
    display.classList.remove("hidden");
    if (typeText) typeText.classList.remove('hidden');
    actions.classList.remove("hidden");
  });

  item.querySelector('[data-role="confirm-delete"]').addEventListener("click", async () => {
    const path = type === "tag" ? `/tags/${itemData.id}` : type === "language" ? `/languages/${itemData.id}` : `/people/${itemData.id}`;
    await request(path, { method: "DELETE" });
    if (type === "tag") {
      await Promise.all([loadTags(), loadFilterOptions(), loadSongs()]);
      showToast("标签已删除", "success");
    } else if (type === "language") {
      await Promise.all([loadLanguages(), loadFilterOptions(), loadSongs()]);
      showToast("语言已删除", "success");
    } else {
      await Promise.all([loadPeople(), loadSongs()]);
      showToast("艺人已删除", "success");
    }
  });

  return item;
}

function renderTagManager() {
  if (!els.tagManagerList || !els.tagSearchInput) return;
  els.tagManagerList.innerHTML = "";
  const keyword = (els.tagSearchInput.value || "").trim().toLowerCase();
  const tags = (state.tags || []).filter((tag) => !keyword || (tag.name || "").toLowerCase().includes(keyword));
  if (!tags.length) {
    els.tagManagerList.innerHTML = '<p class="empty">暂无标签</p>';
  } else {
    tags.forEach((tag) => {
      els.tagManagerList.appendChild(createInlineManagerItem(tag, "tag"));
    });
  }
}

function renderLanguageManager() {
  if (!els.languageManagerList || !els.languageSearchInput) return;
  els.languageManagerList.innerHTML = "";
  const keyword = (els.languageSearchInput.value || "").trim().toLowerCase();
  const languages = (state.languages || []).filter((language) => !keyword || (language.name || "").toLowerCase().includes(keyword));
  if (!languages.length) {
    els.languageManagerList.innerHTML = '<p class="empty">暂无语言</p>';
  } else {
    languages.forEach((language) => {
      els.languageManagerList.appendChild(createInlineManagerItem(language, "language"));
    });
  }
}

function renderPeopleManager() {
  if (!els.peopleManagerList || !els.peopleSearchInput) return;
  els.peopleManagerList.innerHTML = "";
  const keyword = (els.peopleSearchInput.value || "").trim().toLowerCase();
  const people = (state.people || []).filter((person) => !keyword || (person.name || "").toLowerCase().includes(keyword));
  if (!people.length) {
    els.peopleManagerList.innerHTML = '<p class="empty">暂无艺人</p>';
  } else {
    people.forEach((person) => {
      els.peopleManagerList.appendChild(createInlineManagerItem(person, "person"));
    });
  }
}

async function loadFilterOptions() {
  try {
    state.filters = await request("/admin/filter-options");
  } catch (err) {
    state.filters = { formats: [], lead_artists: [], chorus_artists: [], tags: [], languages: [], lyricists: [], composers: [] };
    showToast("加载筛选选项失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  const f = state.filters || {};
  if (els.formatFilter) renderSelectOptions(els.formatFilter, f.formats || [], (v) => v.toUpperCase());
  if (els.leadArtistFilter) renderSelectOptions(els.leadArtistFilter, f.lead_artists || []);
  if (els.chorusArtistFilter) renderSelectOptions(els.chorusArtistFilter, f.chorus_artists || []);
  if (els.tagFilter) els.tagFilter.innerHTML = ['<option value="">全部</option>', ...(f.tags || []).map((tag) => `<option value="${tag.id}">${tag.name}</option>`)].join("");
  if (els.languageFilter) els.languageFilter.innerHTML = ['<option value="">全部</option>', ...(f.languages || []).map((language) => `<option value="${language.name}">${language.name}</option>`)].join("");
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
}

async function loadLanguages() {
  try {
    state.languages = await request("/languages");
  } catch (err) {
    state.languages = [];
    showToast("加载语言失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  if (els.languageInput && Array.isArray(state.languages)) {
    els.languageInput.innerHTML = state.languages.map((language) => `<option value="${language.id}">${language.name}</option>`).join("");
  }
  renderLanguageManager();
}

async function loadPeople() {
  try {
    state.people = await request("/people");
  } catch (err) {
    state.people = [];
    showToast("加载艺人失败: " + (err && err.message ? err.message : String(err)), "error");
  }
  if (els.leadArtistInput) renderArtistMultiSelect(els.leadArtistInput, getSelectedArtistIds(els.leadArtistInput));
  if (els.chorusArtistInput) renderArtistMultiSelect(els.chorusArtistInput, getSelectedArtistIds(els.chorusArtistInput));
  if (els.lyricistInput) renderArtistMultiSelect(els.lyricistInput, getSelectedArtistIds(els.lyricistInput), "作词");
  if (els.composerInput) renderArtistMultiSelect(els.composerInput, getSelectedArtistIds(els.composerInput), "作曲");
  renderPeopleManager();
}

async function loadSongs() {
  try {
    const params = new URLSearchParams();
    if (els.keywordInput && els.keywordInput.value.trim()) params.set("keyword", els.keywordInput.value.trim());
    if (els.formatFilter && els.formatFilter.value) params.append("formats", els.formatFilter.value);
    if (els.leadArtistFilter && els.leadArtistFilter.value) params.append("lead_artists", els.leadArtistFilter.value);
    if (els.chorusArtistFilter && els.chorusArtistFilter.value) params.append("chorus_artists", els.chorusArtistFilter.value);
    if (els.tagFilter && els.tagFilter.value) params.append("tag_ids", els.tagFilter.value);
    if (els.languageFilter && els.languageFilter.value) params.append("languages", els.languageFilter.value);
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
  els.scanBtn.disabled = true;
  els.scanBtn.textContent = "扫描中...";
  try {
    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("files", file, file.webkitRelativePath || file.name));
    const result = await request("/admin/import-directory", {
      method: "POST",
      body: formData,
    });
    els.scanSummary.textContent = `扫描完成：扫描 ${result.scanned_count}，新增 ${result.added_count}，跳过 ${result.skipped_count}`;
    await Promise.all([loadFilterOptions(), loadSongs()]);
    showToast("扫描完成", "success");
  } catch (err) {
    showToast(`扫描失败: ${err.message}`, "error");
  } finally {
    els.scanBtn.disabled = false;
    els.scanBtn.textContent = "扫描目录";
    els.directoryPicker.value = "";
  }
}

async function openEditModal(songId) {
  state.editingSongId = songId;
  const detail = await request(`/songs/${songId}`);
  els.titleInput.value = detail.title || "";
  renderArtistMultiSelect(els.leadArtistInput, detail.lead_artist_ids || [], "歌手");
  renderArtistMultiSelect(els.chorusArtistInput, detail.chorus_artist_ids || [], "歌手");
  renderArtistMultiSelect(els.lyricistInput, detail.lyricist_ids || [], "作词");
  renderArtistMultiSelect(els.composerInput, detail.composer_ids || [], "作曲");
  els.albumInput.value = detail.album || "";
  els.durationInput.value = detail.duration_ms || "";
  els.releaseDateInput.value = detail.release_date || "";
  const selectedLanguage = state.languages.find((language) => language.name === detail.language) || state.languages[0];
  if (selectedLanguage) els.languageInput.value = String(selectedLanguage.id);
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
  await request(`/songs/${state.editingSongId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: els.titleInput.value.trim(),
      lead_artist_ids: getSelectedArtistIds(els.leadArtistInput),
      chorus_artist_ids: getSelectedArtistIds(els.chorusArtistInput),
      lyricist_ids: getSelectedArtistIds(els.lyricistInput),
      composer_ids: getSelectedArtistIds(els.composerInput),
      album: els.albumInput.value.trim(),
      duration_ms: els.durationInput.value === "" ? null : Number(els.durationInput.value),
      language_id: Number(els.languageInput.value),
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
[els.formatFilter, els.leadArtistFilter, els.chorusArtistFilter, els.tagFilter, els.languageFilter, els.lyricistFilter, els.composerFilter].forEach((el) => {
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
els.scanBtn.addEventListener("click", () => {
  els.directoryPicker.click();
});
els.directoryPicker.addEventListener("change", () => {
  runScan().catch((err) => showToast(`扫描失败: ${err.message}`, "error"));
});
els.adminNavMusic?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("music"); });
els.adminNavPeople?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("people"); });
els.adminNavTags?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("tags"); });
els.adminNavLanguage?.addEventListener("click", (e) => { e.preventDefault(); showAdminPage("language"); });
els.goFrontendBtn?.addEventListener("click", () => { window.location.href = "/"; });
els.tagSearchInput?.addEventListener("input", renderTagManager);
els.tagNewBtn?.addEventListener("click", () => openCreateModal("tag"));
els.peopleSearchInput?.addEventListener("input", renderPeopleManager);
els.peopleNewBtn?.addEventListener("click", () => openCreateModal("person"));
els.languageSearchInput?.addEventListener("input", renderLanguageManager);
els.languageNewBtn?.addEventListener("click", () => openCreateModal("language"));
els.createForm?.addEventListener("submit", submitCreateForm);
els.createCloseBtn?.addEventListener("click", closeCreateModal);
els.createCancelBtn?.addEventListener("click", closeCreateModal);
els.createOverlay?.addEventListener("click", (e) => { if (e.target === els.createOverlay) closeCreateModal(); });
els.editCloseBtn.addEventListener("click", closeEditModal);
els.editCancelBtn?.addEventListener("click", closeEditModal);
els.editOverlay?.addEventListener("click", (e) => { if (e.target === els.editOverlay) closeEditModal(); });
els.modalCancelBtn.addEventListener("click", () => closeModal(null));
els.modalConfirmBtn.addEventListener("click", () => closeModal(els.modalInputWrap.classList.contains("hidden") ? true : els.modalInput.value));
els.modalOverlay.addEventListener("click", (event) => { 
  event.stopPropagation();
  if (event.target === els.modalOverlay) closeModal(null); 
});
els.modalInput.addEventListener("keydown", (event) => { if (event.key === "Enter") closeModal(els.modalInput.value); });
document.addEventListener("click", () => {
  document.querySelectorAll('.table-more-menu').forEach((node) => node.classList.add("hidden"));
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

Promise.all([loadTags(), loadLanguages(), loadPeople(), loadFilterOptions(), loadSongs()]).catch((err) => {
  showToast("加载失败: " + (err && err.message ? err.message : String(err)), "error");
});
