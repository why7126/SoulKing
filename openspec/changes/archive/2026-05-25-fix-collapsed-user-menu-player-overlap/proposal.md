## Why

`fix-collapsed-user-menu-popout` 已通过方案 A 将收起侧栏时的用户菜单向右浮出轨道并恢复横排可读，但菜单仍使用 `z-index: 30`，而前台底部播放器 `.studio-player` 为 `z-index: 50`、后台试听条为 `z-index: 40`。收起侧栏后菜单水平伸出至主内容区底部，与固定定位的播放器在视口上重叠，导致菜单项被播放器遮挡、无法点击。需要在不改变菜单 HTML/JS 的前提下，修正收起态下的层叠顺序。

## What Changes

- 在 `studio.css` 与 `admin-studio.css` 中，为 `.app-shell.is-sidebar-collapsed` 下的用户菜单（`.sk-user-menu` / `.adm-user-menu`）提升 `z-index`，使其高于对应壳的底部播放器/试听条，且低于模态层（如 `z-index: 200` 的抽屉）。
- 展开侧栏时用户菜单的 `z-index` 保持 `30`（与现网一致）。
- 不新增 API、不修改 HTML 结构或 JavaScript 菜单开关逻辑（延续纯 CSS 方案 A）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `sidebar-user-menu-popout`: 补充收起侧栏时用户菜单 MUST 显示在底部播放器/试听条之上的层叠要求及验收场景。

## Impact

- `app/static/studio.css` — 前台收起态 `.sk-user-menu` 的 `z-index`
- `app/static/admin-studio.css` — 后台收起态 `.adm-user-menu` 的 `z-index`
- 受影响页面：`app/static/index.html`、`app/static/admin.html`（仅视觉层叠，无结构变更）
- 需手动验证：收起侧栏 → 打开用户菜单 → 菜单完整可见且可点击，不被底部播放器遮挡
