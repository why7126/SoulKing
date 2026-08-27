## Why

上一变更将编辑抽屉高度限定为 `.adm-workspace`（表格行）内 100%，与用户预期不符：抽屉应占满**整个右侧主内容区**的可用纵向空间（与 `.app-shell` 同高的 `100vh` 列，底部预留固定播放器高度）。当前实现导致抽屉视觉上短于主内容区，页头/工具栏与抽屉顶部之间存在高度断层，底部操作栏也可能无法稳定贴底。

## What Changes

- 重新定义后台歌曲编辑抽屉（`#adminEditPanel`）的高度语义：打开时 MUST 纵向占满右侧主内容区（`.app-admin-main-wrap` / `#admin-page-music` 可视列），从主内容区顶边至固定底部播放器上沿（`bottom: var(--adm-player-total-h)`），而非仅 `.adm-workspace` 高度。
- 调整布局实现：宽屏下抽屉采用相对主内容区的固定/绝对定位（或等效方案），使抽屉与 `100vh` 主列对齐；窄屏既有 `fixed` 全高行为保持一致并统一变量。
- 修复 flex 滚动链：`.drawer-body-scroll` 补充 `min-height: 0`，确保正文在固定高度面板内滚动、头尾固定。
- **不在本变更范围**：保存草稿移除、影视剧列表列（已在 `admin-drawer-full-height-add-drama-column` 实现）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：后台编辑抽屉全高布局需求——高度参照由 `.adm-workspace` 改为右侧主内容区 `100vh` 列（扣除底部播放器）。

## Impact

- **前端静态资源**：`app/static/admin.html`（若需调整 DOM 挂载点）、`app/static/admin-studio.css`（抽屉定位与高度、滚动链）；可能微调 `app/static/admin.js`（打开/关闭时 class 或布局辅助，若纯 CSS 可不动）。
- **后端 API**：无。
- **与上一变更关系**：修正 `admin-drawer-full-height-add-drama-column` 中抽屉高度的产品语义；该变更中列表列与草稿移除仍有效。
