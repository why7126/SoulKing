## Why

后台歌曲编辑抽屉当前未占满工作区可用高度，表单区与底部操作栏的视觉层级不够清晰；「保存草稿」仅将部分字段写入 `localStorage` 且未在打开抽屉时回显，属于半成品能力，增加操作噪音。与此同时，`film_tv`（影视剧）字段已在 API 与编辑抽屉中可用，但前台与后台歌曲列表均未展示，用户无法在列表中快速浏览该维度信息。

## What Changes

- 后台歌曲管理页右侧编辑抽屉（`#adminEditPanel`）在打开时 MUST 占满 `.adm-workspace` 可用高度（100%），头部、可滚动正文、底部操作栏采用纵向 flex 布局。
- 移除编辑抽屉底部「保存草稿」按钮及其 `localStorage` 写入逻辑（`#saveDraftBtn`、`adm-draft-*`）。
- 后台歌曲列表新增「影视剧」列，位于「标签」列之前；展示 `film_tv`，空值显示「—」；表头排序参数使用 `film_tv`（后端已支持）。
- 前台音乐库歌曲列表新增「影视剧」列，位于「标签」列之前；展示 API 响应中的 `film_tv`，空值显示「—」。
- 更新空列表 `colspan`、冻结列（若有）及横向滚动相关样式以适配新增列。

## Capabilities

### New Capabilities

（无 — 本变更仅调整既有 Web 静态壳行为，不引入新能力域。）

### Modified Capabilities

- `web-static-client-shells`：后台列表列定义与顺序、前台音乐库列表列定义、后台编辑抽屉布局与底部操作区（移除草稿、全高）。

## Impact

- **前端静态资源**：`app/static/admin.html`、`app/static/admin.js`、`app/static/admin-studio.css`、`app/static/index.html`、`app/static/frontend.js`；必要时微调 `app/static/studio.css` 列宽。
- **后端 API**：无需变更；列表响应已含 `film_tv`，`sort_by=film_tv` 已支持。
- **数据模型**：无迁移。
- **规范**：`openspec/specs/web-static-client-shells/spec.md` 中列表列顺序与抽屉布局相关需求将更新。
