## Context

后台壳（`admin.html` + `admin-studio.css` + `admin.js`）中「歌曲管理」已采用 SoulKing Admin 布局：`admin-studio-root` → `adm-page-header` → `adm-controls`（`adm-toolbar` + `adm-search-wrap`）→ `adm-table-scroll` + `adm-table-footer`。艺人、标签、语言、用户四页仍嵌在 `admin-subpage-wrap` 内，工具栏为 Hermes 时代的 `panel` + `admin-search-row` + `search-field-wrap`，表格为 `admin-table` + `admin-table-wrap`，批量删除使用 `btn danger`，页头带内联 `style` 去边框。

`ui-design.md` 已定义 `--adm-*` 令牌与 `btn-adm-*` 组件；`user-administration` 规范要求用户管理页与标签/语言管理一致——本次将统一基准提升为与歌曲管理相同的 Admin 体系。

## Goals / Non-Goals

**Goals:**

- 四页（艺人、标签、语言、用户）主内容区 DOM 结构与类名对齐歌曲管理页的 Admin 模式。
- 搜索、主操作、批量危险操作、表头排序、表格容器、底栏（总数 + 分页，若适用）视觉与歌曲页一致。
- 用户管理增加用户名/昵称客户端搜索，工具栏与其它参考数据页同构。
- `manager-sort-btn` 保留 `data-manager` / `data-sort` 供 `admin.js` 复用，样式合并到 Admin 表头排序外观（可与 `sort-btn` 共享规则或别名）。
- 更新 `ui-design.md` Admin 节，记录参考数据管理页布局约定。

**Non-Goals:**

- 不修改 `/people`、`/tags`、`/languages`、`/admin/users` 等 API。
- 不改造歌曲管理页、编辑抽屉、底部播放器。
- 不强制本次对齐「风格管理」页（结构相同，可作为 follow-up 复用同一模板，除非实现时改动成本极低）。
- 不引入新的服务端分页（若当前列表为全量加载，可仅做客户端分页或先对齐底栏样式与「共 N 条」文案）。

## Decisions

### 1. 页面根容器统一为 `admin-studio-root`

**选择**：四页 `section` 内层由 `admin-subpage-wrap` 改为 `admin-studio-root`，与 `#admin-page-music` 一致。

**理由**：复用已有 padding、overflow 与页头间距规则，避免继续维护 `admin-subpage-wrap` 特例。

**备选**：仅 CSS 覆盖 `admin-subpage-wrap` 外观——无法统一搜索框与底栏结构，维护成本高。

### 2. 工具栏复用 `adm-controls` + `adm-toolbar`

**选择**：每页工具栏使用 `adm-controls admin-toolbar-panel` > `adm-toolbar` > `adm-search-wrap`（含 SVG 搜索图标与清空按钮）+ `adm-toolbar-actions`（新建、批量删除等）。

**理由**：与歌曲管理、前台音乐库工具栏模式一致；`adm-search-wrap` 已含 focus、清空按钮定位。

**用户管理**：新增 `#userSearchInput`（及清空按钮），`admin.js` 在 `renderUsers` 前按用户名/昵称子串过滤（大小写不敏感）。

### 3. 表格容器与表类名

**选择**：表格外层使用 `adm-table-scroll admin-table-panel`，表格增加 `adm-ref-table`（或复用 `adm-songs-table` 的非歌曲专用别名 `adm-data-table`）以共享表头/行 hover/边框样式；不复制 17 列歌曲表规则。

**理由**：歌曲表含冻结列等专用规则，参考数据表列数少，需独立但同源的表格样式块。

**实现**：在 `admin-studio.css` 增加 `.admin-app .adm-data-table`（或 `.adm-ref-table`），从 `.adm-songs-table` 抽取通用 thead/tbody/empty-cell 规则，歌曲表 `@extend` 或并列选择器包含两者。

### 4. 排序按钮样式收敛

**选择**：`.manager-sort-btn` 与 `.sort-btn` 在 `admin-studio.css` 使用组合选择器共享样式；HTML 可保留 `manager-sort-btn` 类以减少 JS 改动。

**理由**：`admin.js` 中 `manager-sort-btn` 点击委托与 `data-manager` 逻辑已稳定。

### 5. 危险与批量操作按钮

**选择**：`peopleBatchDeleteBtn` 等由 `btn danger hidden` 改为 `btn-adm-ghost btn-adm-danger`（或项目内已有的 Admin 危险 ghost 模式）；显示逻辑仍为 `hidden` 切换。

**理由**：符合 `ui-design.md` 3.3 按钮约定。

### 6. 底栏与分页

**选择**：艺人/标签/语言若当前为全量渲染，增加与歌曲页同结构的 `adm-table-footer`：`adm-list-total` + 可选 `adm-pagination`（每页 20/50/100）；分页逻辑在 `admin.js` 各 `render*` 函数旁增加轻量 state（`peoplePage` 等）或抽取共用 `paginateRows(rows, page, size)`。

**用户管理**：同样增加底栏；若列表较短可固定每页 20。

**备选**：仅加「共 N 条」无底部分页——歌曲页已有分页，不对齐会显得仍不一致；优先客户端分页。

### 7. 清理 Hermes 内联与冗余 panel

**选择**：去掉页头 `style="border:0;padding-top:0"`；删除双层 `panel` 包裹，改为 Admin 单层 `adm-controls` + `adm-main-column` 结构。

**理由**：内联样式无法响应主题令牌。

## Risks / Trade-offs

- **[DOM 变更导致 admin.js 选择器失效]** → 更新 `els` 初始化与 `querySelector`；改完后在四页各执行一次新建/编辑/删除/批量删除冒烟。
- **[分页引入行为变化]** → 默认每页 20 与歌曲页一致；全选 checkbox 仅作用于当前页（与歌曲列表一致）或在规范中明确；实现时与歌曲页 `selectAll` 行为对齐。
- **[styles.css 中 manager-* 规则成为死代码]** → 实现后 grep 确认无引用再删或保留注释「deprecated」。
- **[用户搜索与后端分页未来冲突]** → 当前用户量小，客户端过滤足够；API 不变。

## Migration Plan

1. 在 `admin-studio.css` 增加参考数据表与 `manager-sort-btn` 样式合并。
2. 按页改写 `admin.html`（people → tags → language → users）。
3. 调整 `admin.js` 渲染模板（行内 class）、`els`、搜索/分页/全选逻辑。
4. 更新 `ui-design.md`。
5. 手动验收四页 + 回归歌曲管理页未受影响。

无数据迁移；静态资源部署即生效。回滚为还原 HTML/CSS/JS 三文件。

## Open Questions

- 风格管理页是否在本变更一并套用同一模板（建议实现阶段若 diff 可复用则一并完成，否则单独小变更）。
