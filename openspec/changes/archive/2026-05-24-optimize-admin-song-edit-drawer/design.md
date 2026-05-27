## Context

后台歌曲管理页（`admin.html` + `admin.js` + `admin-studio.css`）使用右侧内嵌面板 `#adminEditPanel`（`.admin-edit-panel`）编辑元数据，默认宽度 `--adm-edit-w: 380px`。

当前状态：

| 字段 | 现状 | 目标 |
|------|------|------|
| 艺人 | 单一「艺人」+ `leadArtistInput`（`renderArtistMultiSelect`，类型「歌手」） | 原唱 / 作词 / 作曲 三字段并列可见 |
| 作词、作曲 | 已有 `lyricistInput` / `composerInput`，但包在 `adm-hidden-filters` | 移出隐藏区，交互与语言一致 |
| 语言 | `renderLanguageMultiSelect`：搜索、多选、新建、最近排序 | 作为艺人/标签的参考实现 |
| 标签 | `renderTagOptions` 平铺 checkbox（`#singleTagOptions`） | 改为 `multi-select` |
| 格式 | `#editFormatDisplay` 只读文本，常只显示首个文件 | 从全部 `files[].format` 聚合，且不在表单中占编辑位 |

后端已支持 `lead_artist_ids`、`lyricist_ids`、`composer_ids`、`language_ids`、`tag_ids` 及多文件 `files[]`，无需 API 变更。

## Goals / Non-Goals

**Goals:**

- 抽屉主表单字段与列表列语义对齐（原唱、作词、作曲、标签）。
- 原唱/作词/作曲/标签均采用与语言相同的多选 UX（模糊搜索、多选、输入新建、chip 触发器）。
- 加宽编辑面板，避免多选下拉与三列艺人挤压。
- 格式由关联音频文件自动推导，支持多格式并列展示；用户不可在抽屉内编辑格式。

**Non-Goals:**

- 不改造影视剧、风格字段的产品策略（可维持 `adm-hidden-filters`）。
- 不修改列表「格式」列的展示规则（本变更仅抽屉内）。
- 不新增后端格式字段或迁移历史数据。
- 不重做 AI 解析区、音频文件行的交互（除添加/删除文件后刷新格式展示）。

## Decisions

### 1. 艺人三字段：复用 `renderArtistMultiSelect`，仅调整布局与文案

**选择**：继续调用 `renderArtistMultiSelect(container, ids, type)`，`type` 分别为「歌手」（原唱）、「作词」、「作曲」；从 `adm-hidden-filters` 移除作词/作曲，将原唱标签由「艺人」改为「原唱」。

**理由**：该函数已实现模糊搜索、多选、同名艺人补类型、新建艺人，与语言模式等价；避免重复实现。

**备选**：抽取通用 `renderReferenceEntityMultiSelect` —— 收益有限，可留作后续重构。

### 2. 标签：新增 `renderTagMultiSelect`，对齐 `renderLanguageMultiSelect`

**选择**：将 `#singleTagOptions` 容器改为 `class="multi-select"`（如 `#tagInput`），实现 `renderTagMultiSelect(selectedIds)`：数据源 `state.tags`，新建走 `POST /tags`，最近使用 key `pm_admin_tag_recent_v1`，占位符「搜索、筛选或输入新标签…」。

**理由**：与语言一致，满足模糊搜索 + 多选 + 新建；保存时仍提交 `tag_ids`（与现有 `renderTagOptions` + 保存逻辑对齐）。

**备选**：保留平铺 checkbox —— 标签增多时可读性与可发现性差。

### 3. 格式：移除表单字段，只读聚合区

**选择**：

- 从 `adm-form-grid-2` 中 **删除** `#editFormatDisplay` 表单项。
- 新增工具函数 `formatsFromDetailFiles(files)`：从 `detail.files` 提取 `format`，去重、小写归一、大写展示，用 ` / ` 连接（与列表 `formatSongFormatLabel` 多格式分支一致）。
- 在「音频文件」区块标题旁或区块顶部展示只读格式 chips（无输入框）；`openEditModal` 在 `preserveMetadata` 与添加/删除文件后均刷新该展示。

**理由**：格式本质是文件属性，用户编辑元数据不应改格式；多文件场景下列表已支持 `formats` 数组。

### 4. 抽屉宽度

**选择**：将 `--adm-edit-w` 从 `380px` 调整为 **`480px`**（实现时可按视觉微调至 460–520px）；窄屏仍使用 `min(100vw, var(--adm-edit-w))`。

**理由**：三列艺人 + 宽 multi-select 菜单需要约 100px 以上增量；过大则挤压列表区。

### 5. 表单栅格

**选择**：原唱/作词/作曲使用 `.adm-form-grid-3`（三列等分）；专辑、发行日期、语言保持两列或单列；标签独占一行 `form-field`。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 重复绑定 `multi-select` 事件导致内存泄漏 | `render*` 时 `innerHTML = ""` 重建（与语言一致） |
| 标签新建与列表筛选选项不同步 | 新建后 `loadTags()` + `populateQuickFilterOptions()` |
| 移除格式输入后用户找不到格式信息 | 音频区顶部 chips + 每行 variant 仍显示格式 |
| 抽屉变窄列表区 | 480px 为折中；用户可关闭抽屉 |

## Migration Plan

纯前端静态资源变更：更新 `admin.html` / `admin.js` / `admin-studio.css` 并递增 `?v=` 缓存参数。无数据库迁移。部署后刷新后台即可。

## Open Questions

（无 — 需求已明确。）
