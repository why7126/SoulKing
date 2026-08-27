## Why

歌曲管理页在完成列扩展与服务端分页后，出现整页纵向滚动、表底分页不易见、表底左侧重复批量按钮、「共 N 首」位置不符合预期，以及更新时间/操作列在宽表下被横向裁切等问题，影响日常浏览与操作效率。

## What Changes

- **消除页面级纵向滚动**：后台歌曲管理页在常见视口高度下，主内容区固定高度，仅表格区域内部滚动；修正 `body` 与 `app-admin-main-wrap` 等与前台共用的 overflow/padding 冲突。
- **表底分页始终可见**：分页栏（含「共 N 首」、页码、每页条数）固定在列表区域底部、视口内可见；无筛选、有数据时亦展示完整分页控件。
- **移除表底批量操作区**：删除表底 `adm-batch-bar`（批量编辑/标签/待修复/删除等）；批量能力保留在顶部工具栏。
- **「共 N 首」左对齐**：表底左侧展示筛选结果总数文案；右侧为分页控件（上一页、页码、下一页、每页条数）。
- **更新时间列与操作列可见**：操作列右侧冻结（sticky）并加宽以容纳编辑、播放、下载、更多（含删除）；保证横向滚动时仍能看到更新时间与操作按钮。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充/调整歌曲管理页布局滚动、表底栏结构、总数文案位置、操作列冻结与可见性要求。

## Impact

- **前端**：`app/static/admin.html`、`app/static/admin.js`、`app/static/admin-studio.css`、`app/static/styles.css`（后台相关选择器）。
- **后端 / API**：无变更。
- **OpenSpec**：`openspec/specs/web-static-client-shells/spec.md` 增量。
