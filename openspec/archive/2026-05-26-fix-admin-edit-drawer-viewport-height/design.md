## Context

后台 `.app-shell` 为 `height: 100vh`；右侧 `.app-admin-main-wrap` 占满除侧栏外的列。歌曲管理页 `#admin-page-music` 内结构为：

```
.admin-studio-root
  ├── .adm-page-header
  ├── .adm-controls（工具栏 + 筛选）
  ├── .adm-workspace（表格 + #adminEditPanel 内嵌 flex 兄弟）
  └── #adminStudioPlayer（position: fixed 贴底，left 随侧栏宽度）
```

上一实现将 `#adminEditPanel.is-open` 设为 `height: 100%` 相对 `.adm-workspace`，抽屉仅与表格行同高，不包含页头/工具栏区域。用户要求抽屉相对**整个右侧主内容区**纵向占满（等效 `100vh` 主列高度，扣除底部播放器 `--adm-player-total-h`）。

另：`admin-studio.css` 中 `.admin-edit-panel .drawer-body-scroll` 覆盖全局样式时缺少 `min-height: 0`，可能导致 flex 内滚动失效。

## Goals / Non-Goals

**Goals:**

- 打开编辑抽屉时，面板顶边对齐右侧主内容区顶边（视口 `top: 0`），底边对齐固定播放器上沿（`bottom: var(--adm-player-total-h)`）。
- 面板内 `.drawer-head` / `.drawer-footer` 固定，`.drawer-body-scroll` 占剩余高度并可滚动。
- 抽屉打开时，主内容（页头、工具栏、表格）右侧预留 `--adm-edit-w` 宽度，避免表格被遮挡。
- 侧栏折叠时抽屉 `right: 0` 仍正确；播放器 `left` 随侧栏变量已有，抽屉不与侧栏重叠。

**Non-Goals:**

- 不改为全屏 modal 或覆盖侧栏。
- 不改动抽屉字段、保存草稿（已移除）、列表列。
- 不重做窄屏 ≤1100px 以下交互，仅统一高度计算与桌面行为。

## Decisions

### 1. 宽屏定位：`position: fixed` + 主内容区 `margin-right`

**选择**：`.admin-edit-panel.is-open` 使用：

```css
position: fixed;
top: 0;
right: 0;
bottom: var(--adm-player-total-h);
width: var(--adm-edit-w);
z-index: 30; /* 高于表格 sticky，低于 modal */
```

打开抽屉时由 JS 为 `#admin-page-music` 增加类（如 `is-edit-drawer-open`），对 `.admin-studio-root` 或等价容器设置 `margin-right: var(--adm-edit-w)`，保留表格可布局空间。

**理由**：无需移动 DOM；与现有 `@media (max-width: 1100px)` 的 fixed 抽屉模式一致，仅统一 `bottom` 与桌面默认行为。`fixed` + `top/bottom` 天然得到主内容区全高。

**备选**：将 `#adminEditPanel` 提升至 `#admin-page-music` 子级并用 `position: absolute` —— 需改 HTML 与关闭逻辑，收益有限。

**备选**：继续 flex 内嵌 + `height: 100%` —— 无法满足「含页头/工具栏的主内容区全高」语义。

### 2. 打开/关闭时切换布局类

**选择**：在 `openEditPanel` / `closeEditPanel`（`admin.js`）中为 `#admin-page-music` 切换 `is-edit-drawer-open`。

**理由**：纯 CSS 无法感知抽屉开关以预留 `margin-right`；改动面小。

### 3. 滚动链修复

**选择**：为 `.admin-edit-panel .drawer-body-scroll` 显式添加 `min-height: 0`；保留 `.drawer-form { flex: 1; min-height: 0 }`；移除仅适用于 flex 内嵌的 `align-self: stretch; height: 100%`（fixed 模式下由 top/bottom 约束高度）。

### 4. 与窄屏媒体查询合并

**选择**：将 `@media (max-width: 1100px)` 中抽屉 fixed 规则与桌面规则合并为同一基础选择器，媒体查询仅处理 `width: min(100vw, var(--adm-edit-w))` 与阴影等差异；`bottom: var(--adm-player-total-h)` 两档一致。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| fixed 抽屉遮挡 sticky 表头列 | z-index 分层；margin-right 保证主内容不被挡 |
| 打开抽屉时 margin 导致横向抖动 | `transition` 与面板 width 同步（可选） |
| 播放器高度变量变化 | 统一使用 `--adm-player-total-h` |
| 其它 admin 子页误受影响 | 选择器限定 `#admin-page-music` |

## Migration Plan

纯前端：`admin-studio.css`、`admin.js`（toggle class）；递增 `?v=`。无后端变更。部署后硬刷新后台即可。

## Open Questions

（无 — 高度语义已明确为右侧主内容区全高至播放器上沿。）
