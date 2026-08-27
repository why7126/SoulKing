## Why

曲库数据模型与 API 已支持歌曲「风格」（`genre` / `genre_ids`），风格管理页与编辑抽屉内的多选组件也已实现，但前后台歌曲列表未展示风格列、快速筛选未提供风格维度，且后台编辑抽屉将风格字段放在 `adm-hidden-filters` 隐藏区。用户无法在列表浏览与筛选中按风格工作，编辑时也不易发现该字段，与语言等元数据字段的体验不一致。

## What Changes

- **后台歌曲列表**：在「语言」列之后新增「风格」列，展示 `genre` 展示名；空值显示「—」；表头支持排序（`sort_by=genre`）。
- **后台更多筛选**：在「语言」筛选之后新增「风格」多选下拉，交互与现有筛选项一致（可搜索、多选）；选项取自风格管理（`/genres`）；筛选通过列表 API 的 `genre_ids` 在服务端生效（同维度 OR）。
- **前台音乐库列表**：在「语言」列之后新增「风格」列，展示 `genre`。
- **前台更多筛选**：在「语言」之后新增「风格」多选筛选，交互与后台对齐；条件提交至曲库列表 API 并在服务端过滤。
- **后台编辑抽屉**：将「风格」字段移出 `adm-hidden-filters`，置于主表单可见区域，布局与交互与「语言」字段一致（`multi-select`：搜索、多选、可新建风格并选中）；保存时继续提交 `genre_ids`。
- **后端（小改）**：列表排序映射增加 `genre` 键；确认 `GET /songs` 在传入 `genre_ids` 时过滤行为不变（已实现则仅补排序）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充前后台歌曲列表风格列与列顺序；扩展快速筛选为七维（含风格，位于语言之后）；扩展筛选项来源表含风格管理；后台编辑抽屉风格字段可见性与语言字段对齐。

## Impact

- **前端**：`app/static/admin.html`、`app/static/admin.js`、`app/static/index.html`、`app/static/frontend.js`；必要时 `app/static/styles.css` / `admin-studio.css` / `studio.css` 列宽微调。
- **后端**：`app/main.py`（`list_songs` 排序映射增加 `genre`；可选增加 `genres` 名称查询参数以与 `languages` 对称，若实现则优先于仅客户端 id 映射）。
- **OpenSpec**：`openspec/specs/web-static-client-shells/spec.md` 增量需求。
- **数据/API**：复用现有 `Genre`、`SongGenre`、`/genres`、`genre_ids` 查询参数，无新表。
