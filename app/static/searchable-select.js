/** Shared searchable <select> UI for front/admin quick filters. */

let activeSearchableSelectMenu = null;

export function getActiveSearchableSelectMenu() {
  return activeSearchableSelectMenu;
}

export function clearActiveSearchableSelectMenu() {
  if (!activeSearchableSelectMenu) return;
  activeSearchableSelectMenu.classList.add("hidden");
  activeSearchableSelectMenu = null;
}

export function closeActiveSearchableSelectMenuOnOutsideClick(target) {
  if (!activeSearchableSelectMenu) return;
  const host = activeSearchableSelectMenu.closest(".searchable-select");
  if (!host || !host.contains(target)) clearActiveSearchableSelectMenu();
}

export function filterDropdownSelectedRawValues(selectEl) {
  if (!selectEl?.options) return [];
  if (!selectEl.multiple) {
    const v = selectEl.value;
    return v ? [v] : [];
  }
  const all = Array.from(selectEl.options);
  const selected = all.filter((o) => o.selected).map((o) => o.value);
  if (selected.length === 0 || selected.length === all.length) return [];
  return selected;
}

/** 全部勾选与未勾选等价于不筛选；归一为全不选 */
export function filterMultiselectNormalizeAllSelected(selectEl) {
  if (!selectEl?.multiple) return;
  const all = Array.from(selectEl.options);
  if (all.length > 1 && all.every((o) => o.selected)) {
    all.forEach((o) => {
      o.selected = false;
    });
  }
}

export function fuzzyMatchName(text, query) {
  const t = (text || "").toLowerCase();
  const q = (query || "").trim().toLowerCase();
  if (!q) return true;
  if (t.includes(q)) return true;
  let i = 0;
  for (let j = 0; j < t.length && i < q.length; j += 1) {
    if (t[j] === q[i]) i += 1;
  }
  return i === q.length;
}

export function syncSearchableSelectTrigger(selectEl) {
  const wrap = selectEl.closest(".searchable-select");
  const trigger = wrap?.querySelector(".searchable-select-trigger");
  if (!trigger) return;
  const emptyLabel = selectEl.dataset.filterLabel || "全部";
  if (selectEl.multiple) {
    const allOpts = Array.from(selectEl.options);
    const selected = allOpts.filter((o) => o.selected);
    if (selected.length === 0 || selected.length === allOpts.length) {
      trigger.textContent = emptyLabel;
      return;
    }
    if (selected.length === 1) {
      trigger.textContent = selected[0].textContent;
      return;
    }
    const labels = selected.map((o) => o.textContent.trim());
    const joined = labels.join("、");
    trigger.textContent = joined.length > 40 ? `已选 ${selected.length} 项` : joined;
    return;
  }
  const idx = selectEl.selectedIndex;
  const opt = idx >= 0 ? selectEl.options[idx] : null;
  trigger.textContent = opt ? opt.textContent : emptyLabel;
}

export function refreshSearchableSelectOptions(selectEl) {
  const wrap = selectEl.closest(".searchable-select");
  if (!wrap) return;
  const menu = wrap.querySelector(".searchable-select-menu");
  const optionsEl = menu?.querySelector(".searchable-select-options");
  const searchInput = menu?.querySelector(".searchable-select-search");
  if (!optionsEl || !searchInput) return;

  const rebuild = () => {
    const kw = (searchInput.value || "").trim();
    const rows = Array.from(selectEl.options).map((o, index) => ({
      value: o.value,
      label: o.textContent,
      opt: o,
      index,
    }));
    const filtered = !kw ? rows : rows.filter((r) => fuzzyMatchName(r.label, kw) || fuzzyMatchName(String(r.value), kw));
    optionsEl.innerHTML = "";
    if (!filtered.length) {
      const empty = document.createElement("div");
      empty.className = "searchable-select-empty muted";
      empty.textContent = "无匹配项";
      optionsEl.appendChild(empty);
      return;
    }
    const sid = selectEl.id || "ss";
    for (const r of filtered) {
      if (selectEl.multiple) {
        const row = document.createElement("div");
        row.className = "searchable-select-check-row";
        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.checked = r.opt.selected;
        cb.id = `${sid}-opt-${r.index}`;
        const span = document.createElement("span");
        span.className = "searchable-select-check-label";
        span.textContent = r.label;
        row.appendChild(cb);
        row.appendChild(span);
        const applyCheckboxToOption = () => {
          r.opt.selected = cb.checked;
          filterMultiselectNormalizeAllSelected(selectEl);
          selectEl.dispatchEvent(new Event("change", { bubbles: true }));
          syncSearchableSelectTrigger(selectEl);
          wrap._searchableRebuild && wrap._searchableRebuild();
        };
        cb.addEventListener("click", (e) => e.stopPropagation());
        cb.addEventListener("change", () => applyCheckboxToOption());
        row.addEventListener("click", (e) => {
          e.stopPropagation();
          if (!e.isTrusted) return;
          if (e.target === cb) return;
          cb.click();
        });
        optionsEl.appendChild(row);
        continue;
      }
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "searchable-select-option";
      btn.setAttribute("role", "option");
      btn.textContent = r.label;
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        selectEl.value = r.value;
        selectEl.dispatchEvent(new Event("change", { bubbles: true }));
        menu.classList.add("hidden");
        if (activeSearchableSelectMenu === menu) activeSearchableSelectMenu = null;
        syncSearchableSelectTrigger(selectEl);
      });
      optionsEl.appendChild(btn);
    }
  };
  wrap._searchableRebuild = rebuild;
  rebuild();
  syncSearchableSelectTrigger(selectEl);
}

export function ensureSearchableSelect(selectEl) {
  if (!selectEl || selectEl.dataset.searchableBound === "1") return;
  selectEl.dataset.searchableBound = "1";
  const wrap = document.createElement("div");
  wrap.className = "searchable-select";
  const parent = selectEl.parentNode;
  parent.insertBefore(wrap, selectEl);
  wrap.appendChild(selectEl);
  selectEl.classList.add("searchable-select-native");

  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "searchable-select-trigger";
  trigger.setAttribute("aria-haspopup", "listbox");

  const menu = document.createElement("div");
  menu.className = "searchable-select-menu hidden";
  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.className = "searchable-select-search";
  searchInput.placeholder = selectEl.dataset.filterLabel ? `搜索${selectEl.dataset.filterLabel}…` : "输入关键字筛选…";
  searchInput.autocomplete = "off";
  const optionsEl = document.createElement("div");
  optionsEl.className = "searchable-select-options";
  menu.appendChild(searchInput);
  menu.appendChild(optionsEl);
  wrap.appendChild(trigger);
  wrap.appendChild(menu);

  searchInput.addEventListener("click", (e) => e.stopPropagation());
  searchInput.addEventListener("input", () => wrap._searchableRebuild && wrap._searchableRebuild());

  trigger.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (activeSearchableSelectMenu && activeSearchableSelectMenu !== menu) {
      activeSearchableSelectMenu.classList.add("hidden");
      activeSearchableSelectMenu = null;
    }
    const willOpen = menu.classList.contains("hidden");
    menu.classList.toggle("hidden", !willOpen);
    activeSearchableSelectMenu = willOpen ? menu : null;
    if (willOpen) {
      searchInput.value = "";
      refreshSearchableSelectOptions(selectEl);
      setTimeout(() => searchInput.focus(), 0);
    }
  });

  selectEl.addEventListener("change", () => syncSearchableSelectTrigger(selectEl));
}
