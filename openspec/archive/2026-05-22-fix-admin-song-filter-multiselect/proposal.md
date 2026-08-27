## Why

后台歌曲管理页的「更多筛选」已改为可搜索多选下拉（`searchable-select`），但用户点击选项后勾选状态无法保持，筛选体验不可用。根因是选项重建流程在恢复选中后又调用 `initAdminFilterMultiSelectDefault` 清空全部选中；此外每次 `renderSongs` 都会重建筛选项 DOM，造成闪烁与多余开销；单选项维度在「全选归一化」逻辑下无法有效勾选。需要在不改动后端 API 的前提下修复客户端筛选交互并明确预期行为。

## What Changes

- **P0**：修复 `populateAdminQuickFilterSelect` 中选中状态被 `initAdminFilterMultiSelectDefault` 立即清空的 bug，使多选勾选/取消勾选与触发器文案正确同步。
- **P1**：将 `populateQuickFilterOptions` 的调用从每次 `renderSongs` / `updateAdminStats` 中解耦，仅在曲库数据或标签等选项来源变更时刷新（如 `loadSongs`、扫描完成、标签/语言变更后）。
- **P2**：调整 `filterMultiselectNormalizeAllSelected`：仅当选项数量大于 1 时，「全部勾选」才等价于「未筛选」；单选项维度允许勾选并保持选中。
- 筛选变更后仍通过 `syncQuickFiltersFromUi` 更新内存 state，列表过滤逻辑不变（同维度 OR、跨维度 AND）。
- 更新静态资源缓存版本号（`admin.js` / 必要时 `admin-studio.css`）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充后台歌曲管理页快速筛选面板的可搜索多选交互要求（勾选持久、选项刷新时机、单选项维度行为）。

## Impact

- **前端**：`app/static/admin.js`（`populateAdminQuickFilterSelect`、`updateAdminStats`、`renderSongs`、`filterMultiselectNormalizeAllSelected`、`populateQuickFilterOptions` 调用链）。
- **样式**：`app/static/admin-studio.css`（如有必要，微调筛选下拉样式；预计改动极小）。
- **后端 / API**：无变更。
- **OpenSpec**：`openspec/specs/web-static-client-shells/spec.md` 增量需求。
