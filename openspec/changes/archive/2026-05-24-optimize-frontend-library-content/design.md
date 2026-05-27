## Context

前台音乐库区块（`index.html` `#songBrowseSection` + `frontend.js` + `studio.css`）当前结构：

- 标题行含「智能排序」与视图切换占位按钮
- Tab 栏：全部歌曲 / 我喜欢的 / 最近播放（后两者仅占位 toast）
- 顶栏 `#headerSearchLibrary` 承载全局搜索；内容区单独一行「展开筛选」按钮
- 筛选面板仅含格式、标签、语言三列
- 表格 7 列：#、歌曲、艺人、专辑、时长、标签、操作

后台歌曲管理（`admin.html` `#admin-page-music`）已收敛为：

- 工具栏一行：搜索框 + 操作按钮区 + 「更多筛选 / 重置」
- 展开面板六维多选：原唱、作词、作曲、标签、格式、语言
- 表格 14 列含原唱/作词/作曲/发行日期等，服务端分页与筛选

用户要求前台音乐库 UI/UE 与后台歌曲管理对齐（搜索+筛选同行、列字段一致 subset），并移除 Tab 与智能排序。

## Goals / Non-Goals

**Goals:**

- 音乐库内容区呈现单一歌曲列表视图，无 Tab 切换
- 搜索框与「更多筛选」「重置」同一工具栏行，视觉与交互模式对齐后台 `adm-toolbar`
- 展开筛选面板六维与后台一致；筛选通过 `/songs` API 查询参数服务端生效
- 表格列：#、歌曲、原唱、作词、作曲、专辑、语言、标签、格式、时长、发行日期、操作
- 保留现有前台行操作（试听、收藏、加入歌单、下载）与分页行为
- 顶栏搜索在音乐库视图下隐藏，避免重复入口；⌘K 快捷键聚焦内容区搜索框

**Non-Goals:**

- 接入「我喜欢的」「最近播放」业务
- 实现智能排序或表头列排序（后台有 sort-btn，前台不要求）
- 网格视图、批量操作、勾选列
- 修改 `/songs` API 或后端筛选逻辑
- 歌单详情页歌曲列表列结构变更（可保持现有或仅做最小 colspan 修正）

## Decisions

### 1. 搜索框位置：从顶栏迁至内容区工具栏

**选择**：在 `#songBrowseSection` 内新增 `studio-library-toolbar`（结构镜像 `adm-toolbar`：搜索 wrap + filter actions），音乐库激活时隐藏 `#headerSearchLibrary`，歌单等其它视图仍使用顶栏搜索。

**理由**：满足「搜索+筛选同一行」且与后台信息架构一致；避免顶栏与内容区双搜索框并存。

**备选**：保留顶栏搜索、内容区仅放筛选 —— 与用户需求及后台模式不一致，不采用。

### 2. 筛选组件复用模式

**选择**：沿用前台已有 `searchable-select` 多选下拉（与后台同类组件），新增 `#filterLeadQuick`、`#filterLyricistQuick`、`#filterComposerQuick` 三个 select；选项来源继续调用 `/admin/filter-options`（与现有 `loadFrontFilters` 一致），六维布局使用与后台相同的横向 flex 面板（`adm-filters` 类或 studio 主题等价样式）。

**理由**：最小改动复用已验证的筛选数据与组件；与后台选项来源一致。

### 3. 表格列与渲染

**选择**：

- 表头静态文本（无 sort-btn，用户未要求排序）
- `songRowInnerHtml` 扩展为 12 列；首列保留 `#` 序号（按当前页偏移 `pageOffset + index + 1`）；歌曲列保留 thumb + title + 播放波形；格式独立列展示 `primaryFormatLabel`；标签列展示 pill；发行日期格式化为 `YYYY-MM-DD` 或 `—`
- 作词/作曲使用与后台相同的 `formatRoleNamesCell` 逻辑（数组 join 或 `—`）

**理由**：字段与后台对齐，前台保持只读浏览态，不引入排序复杂度。

### 4. 移除 Tab 与智能排序

**选择**：删除 DOM、`state.libraryTab`、Tab 事件监听、`#btnSmartSort` 及关联样式；`loadSongs` 不再分支 Tab 逻辑。

**理由**：减少未实现占位 UI，降低维护成本。

### 5. 查询参数扩展

**选择**：`loadSongs` 构建 `URLSearchParams` 时追加 `lead_artists`、`lyricists`、`composers`（与 `admin.js` `buildSongListQueryParams` 同名参数）；保留 `keyword`、`formats`、`tag_ids`、`languages`；继续使用 `limit` + 客户端分页或后续可改为服务端 offset（本变更保持现有前台分页模式，仅扩展筛选维度）。

**理由**：与 API 已有能力对齐，筛选在服务端生效。

### 6. CSS 策略

**选择**：在 `studio.css` 增加 `.studio-library-toolbar`、`.studio-library-filters-panel` 规则，参考 `admin-studio.css` 的 `adm-toolbar` / `adm-filters-panel` 间距与一行布局；表格列宽为新增列设置 `min-width` 与 `text-overflow: ellipsis`，表格区域横向滚动。

**理由**：前台使用 studio 主题色，不直接引用 `body.admin-app` 选择器，但保持布局比例一致。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 列数增多导致窄屏横向滚动 | 表格 wrap 启用 `overflow-x: auto`；次要列 ellipsis |
| 顶栏搜索迁移后 ⌘K 失效 | 更新快捷键 handler 按 `mainNav` 聚焦对应搜索 input |
| 筛选面板 z-index 被表格遮挡 | 工具栏面板 `position: relative; z-index: 2`（对齐后台） |
| 移除 Tab 后用户期望「我喜欢」入口 | proposal 已声明后续单独变更；侧栏统计仍展示曲库总数 |

## Migration Plan

1. 修改 `index.html` DOM 结构，递增 `?v=` 版本号
2. 更新 `frontend.js` 渲染与事件逻辑
3. 补充 `studio.css` 工具栏与表格列样式
4. 硬刷新前台页，手动验收搜索、六维筛选、列展示与分页

## Open Questions

（无）
