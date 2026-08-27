## Context

- 数据层：`Genre`、`SongGenre`、`songs.genre_id` 已存在；`GET /songs` 已支持 `genre_ids` 查询参数与响应字段 `genre`；`PUT` 歌曲元数据已支持 `genre_ids`。
- 后台 `admin.js` 已有 `renderGenreMultiSelect`、`loadGenres`（或等价加载）、编辑保存时提交 `genre_ids`，但 `#genreInput` 位于 `adm-hidden-filters`；列表 `renderSongs` 未渲染风格列；`buildSongListQueryParams` 未附带风格筛选。
- 前台 `frontend.js` 音乐库列表有语言列与语言筛选，无风格列/筛选；详情面板已展示风格。
- 列表排序 `sort_value` 映射含 `language` 但不含 `genre`，表头点击风格排序需后端补齐。

## Goals / Non-Goals

**Goals:**

- 前后台列表在「语言」后展示「风格」列，空值「—」。
- 前后台「更多筛选」在语言后增加风格多选（与 `adm-filter-select` / `studio-filter-select` 一致：Tom Select 或现有封装、可搜索）。
- 风格筛选项来自 `/genres` 管理列表（与语言取自 `/languages` 对称）；参考数据变更后刷新选项并保留仍有效的已选值。
- 筛选请求在服务端通过 `genre_ids` 生效（客户端将所选名称映射为 id，模式同标签 `tag_ids`）。
- 后台编辑抽屉风格字段与语言并排可见，复用现有 `multi-select` 实现。
- 支持 `sort_by=genre` 列表排序。

**Non-Goals:**

- 不改变风格管理页 CRUD、歌单「风格歌单」Tab 逻辑。
- 不将风格改为多值展示列（API 当前 `genre` 为合并展示串，与语言一致）。
- 不新增 `genres` 名称查询参数（除非实现时发现仅 id 映射不足；默认客户端映射即可）。

## Decisions

### 1. 筛选：客户端名称 → `genre_ids`

**选择**：快速筛选 UI 存风格名称数组；`buildSongListQueryParams` / 前台等价函数通过 `state.genres` 映射为 `genre_ids` 追加到查询串。

**理由**：与标签筛选一致；`GET /songs` 已支持 `genre_ids`；无需改 API 契约。

**备选**：新增 `genres: list[str]` 查询参数——与 `languages` 更对称，但属重复能力，本变更不采用。

### 2. 筛选项来源：`state.genres`（`/genres`）

**选择**：`populateQuickFilterOptions` / 前台 `populateFrontFilterOptions` 使用 `state.genres.map(g => g.name)` 升序填充；在 `loadGenres` 完成后刷新，风格 CRUD 后复用现有 reload 链。

### 3. 编辑抽屉布局

**选择**：将 `#genreInput` 的 `form-field` 移入 `adm-form-grid-2`，紧挨「语言」字段（语言左、风格右，或语言下一格为风格）；移除 `adm-hidden-filters` 包裹。

**理由**：与用户需求「与语言字段一样」一致；`renderGenreMultiSelect` 无需重写。

### 4. 列顺序与 colspan

**选择**：后台表头/行在语言与影视剧之间插入风格列；`empty-cell` colspan 由 16 改为 17；冻结列 CSS 若有按列索引需核对（若有 `nth-child` 硬编码则顺延）。

**前台**：在 `sk-col-meta` 语言列后插入风格列；`renderSongRow` 输出 `song.genre`。

### 5. 排序

**选择**：`list_songs` 的 `sort_value` mapping 增加 `"genre": item.genre or ""`；表头 `data-sort="genre"`。

## Risks / Trade-offs

- **[表格变宽]** → 依赖既有横向滚动容器；不新增冻结列除非已有 breakage。
- **[选了风格但曲库无匹配]** → 与语言/标签一致，属预期。
- **[colspan/列数遗漏]** → 任务中显式检查空状态行与排序按钮列表。

## Migration Plan

纯前端 + 小后端排序映射，无数据迁移。部署顺序：先后端（排序键），再静态资源。回滚：还原静态与 `sort_value` 即可。

## Open Questions

（无）
