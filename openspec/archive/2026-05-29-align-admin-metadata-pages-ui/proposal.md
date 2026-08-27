## Why

后台「歌曲管理」页已迁移到 SoulKing Admin（`admin-studio.css`）设计体系：统一页头、统计卡片、`adm-toolbar` 搜索与操作区、`adm-songs-table` 表格与底部分页。而「艺人管理」「标签管理」「语言管理」「用户管理」仍使用早期的 `admin-subpage-wrap` + Hermes `panel` / `admin-search-row` 布局，视觉层级、间距、搜索框、按钮与表头排序样式与歌曲管理明显不一致，削弱后台整体专业感，也增加了维护两套样式的成本。

## What Changes

- 将艺人、标签、语言、用户四个管理页的主内容区结构对齐歌曲管理页的 SoulKing Admin 模式（`admin-studio-root`、`adm-page-header`、`adm-controls` / `adm-toolbar`、`adm-search-wrap`、`adm-table-scroll` 等）。
- 统一工具栏：带搜索图标的搜索框、清空按钮、`btn-adm-primary` / `btn-adm-secondary` / `btn-adm-ghost`；批量删除等危险操作使用 Admin 危险按钮样式，不再使用 Hermes `btn danger`。
- 统一表格与表头：表头排序控件视觉与交互对齐歌曲列表的 `sort-btn`（可保留现有 `manager-sort-btn` 数据属性，样式收敛到 Admin 体系）。
- 为支持客户端分页的参考数据列表（若当前无分页）补充与歌曲管理一致的 `adm-table-footer` + `adm-pagination` 模式，或至少在视觉与间距上与歌曲页底栏一致。
- 用户管理页补充搜索框（按用户名/昵称筛选），与其它参考数据页工具栏结构一致。
- 移除子页页头上的内联 `style` 覆盖，改由 CSS 令牌控制。
- 更新 `ui-design.md` 中后台参考数据管理页的说明（若已有对应章节则修订，否则在 Admin 节补充）。
- **不**改变各管理模块的 API、业务逻辑与权限模型；**不**调整歌曲管理页本身。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：新增后台参考数据管理页（艺人、标签、语言）与用户管理页的 UI/UE 一致性要求，明确须复用 SoulKing Admin 组件模式并与歌曲管理页对齐。
- `user-administration`：修订「后台用户管理界面」要求中关于交互风格的对照基准，从「标签/语言管理页」改为与歌曲管理页及统一后的参考数据管理页一致。

## Impact

- **静态资源**：`app/static/admin.html`、`app/static/admin-studio.css`、`app/static/admin.js`（DOM 结构、类名、可选分页/搜索绑定）。
- **全局样式**：可能缩减 `styles.css` 中仅被子页使用的 `admin-search-row` / `manager-*` 覆盖（保留仍被其它区域引用的规则）。
- **文档**：`ui-design.md`。
- **规范**：`openspec/specs/web-static-client-shells/spec.md`、`openspec/specs/user-administration/spec.md` 增量。
- **无**后端 API、数据库或认证流程变更。
