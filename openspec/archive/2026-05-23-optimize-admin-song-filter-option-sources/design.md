## Context

后台 `admin.js` 中 `populateQuickFilterOptions()` 在刷新快速筛选下拉时：

- **原唱 / 作词 / 作曲**：从 `state.songs` 的 `lead_artist`、`lyricists`、`composers` 去重得到；
- **标签**：合并 `state.tags` 与歌曲上的 `tags`；
- **语言**：从歌曲 `language` 去重；
- **格式**：仍从歌曲文件格式推导（本变更范围外）。

艺人、标签、语言的管理数据已在页面初始化时分别通过 `loadPeople()`、`loadTags()`、`loadLanguages()` 加载到 `state.people`、`state.tags`、`state.languages`。歌曲编辑表单已使用 `peopleByType("歌手"|"作词"|"作曲")` 按类型过滤艺人。快速筛选应复用同一数据源与类型规则，保证与管理页一致。

## Goals / Non-Goals

**Goals:**

- 五个维度（原唱、作词、作曲、标签、语言）的筛选项与对应管理列表一致。
- 艺人维度按 `types` 数组是否包含对应类型过滤（与 `peopleByType` 一致）。
- 选项按名称 `localeCompare(..., "zh-CN")` 升序。
- 参考数据增删改后，在现有 `loadFilterOptions()` / `populateQuickFilterOptions()` 调用链中刷新选项，保留仍有效的已选值。
- 过滤逻辑仍用名称字符串匹配歌曲字段，不改动 OR/AND 语义。

**Non-Goals:**

- 不修改 `/admin/filter-options` 后端聚合接口（可保留供其它用途；快速筛选不再依赖其艺人/标签/语言字段）。
- 不修改「格式」维度数据源。
- 不改变多选交互（已由 `fix-admin-song-filter-multiselect` 覆盖）。

## Decisions

### 1. 复用内存 state，不新增 API

**选择**：在 `populateQuickFilterOptions` 内直接读取已加载的 `state.people`、`state.tags`、`state.languages`。

**理由**：初始化与各管理 CRUD 流程已保证这些数据可用；与歌曲编辑表单一致，零后端改动。

**备选**：扩展 `/admin/filter-options` 按类型返回艺人——增加服务端维护成本，且与前端已有 `state.people` 重复。

### 2. 艺人过滤使用现有 `peopleByType`

**选择**：`peopleByType("歌手")` → 原唱；`"作词"` → 作词；`"作曲"` → 作曲；取 `person.name`。

**理由**：与艺人管理、歌曲表单同一规则；支持一人多类型（出现在多个类型列表中）。

### 3. 标签与语言仅取自管理列表

**选择**：`state.tags.map(t => t.name)`、`state.languages.map(l => l.name)`，不再合并歌曲上的游离值。

**理由**：与用户需求的「召回逻辑」一致——以参考数据为全集；歌曲上存在但未入库管理的名称不应出现在筛选项（若需筛选应先录入管理）。

**权衡**：用户可能选某标签后列表为空（曲库无该标签歌曲）——属预期，与「按权威词表筛选」一致。

### 4. 刷新时机

**选择**：保持 `populateQuickFilterOptions` 在 `loadPeople` / `loadTags` / `loadLanguages` 后的现有调用点；从 `loadSongs`-only 路径移除对该五个维度的重复推导（若仍存在仅因 `renderSongs` 触发的刷新，应已在前序 change 中解耦）。

**补充**：页面初始 `Promise.all` 顺序不变，确保 `populateQuickFilterOptions` 在 people/tags/languages/songs 均就绪后执行。

## Risks / Trade-offs

- **[曲库有、管理无的名称无法筛选]** → 用户需在艺人/标签/语言管理中补录；符合「以管理数据为准」产品意图。
- **[艺人重命名后已选筛选失效]** → 与现行为相同（按名称匹配）；重命名后 `populateQuickFilterOptions` 保留仍存在于新列表的已选值。
- **[空管理列表]** → 下拉无选项；单选项维度场景由既有 P2 逻辑处理。

## Migration Plan

1. 修改 `populateQuickFilterOptions` 五个维度数据源。
2. 确认 `loadPeople` / `loadTags` / `loadLanguages` 后的 `loadFilterOptions` 或 `populateQuickFilterOptions` 调用完整。
3.  bump `admin.js` 查询参数版本。
4. 手动验证：管理页新增艺人/标签/语言后筛选项出现；勾选后列表过滤正确；格式维度不受影响。

## Open Questions

（无）
