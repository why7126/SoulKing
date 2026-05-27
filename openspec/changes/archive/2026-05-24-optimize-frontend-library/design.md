## Context

前台音乐库（`#songBrowseSection`）由 `index.html` + `frontend.js` + `studio.css` 驱动。当前存在：

- 音乐库视图仅隐藏顶栏搜索框，`.studio-top-header` 仍占 56px 空白。
- `loadSongs()` 写死 `limit=500` 且无 `offset`，`renderSongList()` 用 `state.songs.length` 覆盖 `songListTotal`，翻页仅客户端 slice。
- 操作列按钮无居中样式；收藏按钮为占位。
- 播放模式靠 `repeatModeBtn` emoji 循环，与 `shuffleToggleBtn` 功能重叠。
- 「调」、播放器 ♥、详情 ♥ 无业务逻辑。
- 表格横向滚动时 # / 歌曲列未 sticky；后台 admin 已有成熟分页与 sticky 参考实现。

## Goals / Non-Goals

**Goals:**

- 音乐库视图释放顶栏垂直空间，列表区可视面积最大化。
- 分页行为与 `admin.js` 的 `buildSongListQueryParams` + `loadSongs` + `renderPagination` 模式一致。
- 页脚展示清晰分页文案（范围 + 总页数）。
- 操作列视觉对齐；移除所有收藏占位 UI。
- 播放模式通过带中文标签的下拉选择，状态与 `state.playMode` 同步。
- # 与歌曲列横向滚动时冻结。

**Non-Goals:**

- 实现收藏、音质切换、歌词面板、全屏等真实业务功能。
- 修改 `GET /songs` API 契约或后端分页逻辑。
- 歌单详情页分页/布局大改（除非共享组件必须同步）。
- 隐藏「词」「全屏」按钮（本次仅明确「调」与三处收藏）。

## Decisions

### 1. 顶栏：音乐库视图隐藏整个 `studio-top-header`

**选择**：在 `.studio-root.is-library-view` 下对 `.studio-top-header` 设置 `display: none`（或等效 `height:0; overflow:hidden; border:none`）。

**理由**：内容区已有独立搜索/筛选；顶栏在音乐库下无任何可见控件。比仅隐藏 `#headerSearchLibrary` 更彻底。

**替代方案**：保留顶栏放面包屑 — 当前无内容，否决。

**实现要点**：`syncFrontChrome()` 已维护 `is-library-view` class；歌单/专辑等其它视图不受影响。

### 2. 分页：对齐 admin 服务端模式

**选择**：抽取与 admin 等价的 `buildFrontSongListQueryParams()`，含 `offset=(page-1)*pageSize`、`limit=pageSize`；`loadSongs()` 写入 `state.songListTotal = page.total`；翻页/改 pageSize 调用 `loadSongs()`；`renderSongList()` **不再**赋值 `songListTotal`。

**理由**：API 已支持 offset/limit；admin 已验证；避免 500 条上限与 total 被覆盖。

**页脚 UI**：在现有 `#frontSongListTotalLabel` 旁或内增加 `#frontPageInfoLabel`，格式示例：
- `显示 21–40，共 312 首`
- `第 2 / 16 页`

**筛选变更**：重置页码为 1 后 `loadSongs()`（与 admin 一致）；翻页时不重置筛选。

**歌单模式**：`selectedPlaylistId` 非空时仍为客户端过滤歌单曲目；可保留客户端分页或暂不分页（非本次主路径）。

### 3. 操作列：居中 + 移除收藏

**选择**：`.sk-row-actions button` 增加 `display: grid; place-items: center`；从 `songRowInnerHtml` / 事件绑定中删除 `data-role="fav"`。

**理由**：与 `.studio-transport button` 一致；减少误导性占位。

### 4. 播放模式：带标签的下拉（方案 B）

**选择**：在 transport 区用可见 `<select>` 或自定义 popover 替代 emoji 循环按钮，选项：
- 列表循环 (`list-loop`)
- 单曲循环 (`single-loop`)
- 随机播放 (`shuffle`)
- 顺序播放 (`sequence`)

**移除/合并**：删除独立的 `repeatModeBtn` emoji 循环；`shuffleToggleBtn` 移除或改为选中下拉中的「随机」快捷态（推荐 **移除 shuffle 按钮**，避免双入口）。

**实现**：复用已有 `#playModeSelect`（去掉 `hidden`），加 Studio 样式；`change` 事件更新 `state.playMode` 并调用 `syncTransportDecorations()`（可简化为仅高亮当前选项）。

### 5. 占位控件隐藏

**选择**：
- 移除或 `hidden`：播放器 `.sk-player-heart`、`#inspectorFavoriteBtn`、列表 `data-role="fav"`。
- `hidden`：`title="音质"` 的「调」按钮（`sk-pl-aux` 第一个）。

**理由**：无 handler 的单字按钮增加认知负担；收藏统一等能力上线后再加。

### 6. 冻结列：# + 歌曲

**选择**：在 `studio.css` 为 `.studio-library-table` 的 `.sk-col-idx`、`.sk-col-title`（th/td）添加 `position: sticky`，`left: 0` / `left: 44px`，设置背景色与 hover 背景，thead `z-index` 高于 tbody。

**理由**：admin `#admin-page-music` 已有同类模式；前台表格在 `.studio-library-table-wrap` 内横向滚动。

**注意**：确认 `border-collapse: separate`（若 sticky 失效则与 admin 注释一致调整）。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 服务端分页后「播放当前列表」队列仅含当前页 | 保持 `syncQueue()` 语义：队列可仍为当前页或全量；实现时文档化——若需「播放全部筛选结果」可后续用无 limit 请求 |
| sticky 列在深色主题下滚动透底 | 显式设置 `--sk-sticky-bg` 与 hover 色 |
| 隐藏顶栏后 ⌘K 仍须聚焦内容区搜索 | 现有 shortcut 已指向 `libraryKeywordInput`，回归验证 |
| 移除 shuffle 按钮改变老用户习惯 | 下拉中有「随机播放」且更明确 |

## Migration Plan

1. 静态资源改动，随下次部署生效；无数据库迁移。
2. 回滚：还原 `index.html` / `frontend.js` / `studio.css` 三文件即可。
3. 验收：音乐库 >20 首时分页翻页；横向滚动冻结列；播放器模式下拉；无顶栏空白。

## Open Questions

- 「播放当前列表」(`#playPlaylistBtn`) 是否应对全量筛选结果建队列而非当前页？（建议实现阶段与产品确认，默认对齐 admin：当前页。）
