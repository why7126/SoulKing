## Why

侧边栏收起至 64px 轨道时，底部用户头像的下拉菜单仍使用 `left: 6px; right: 6px` 锚定在侧栏内，可用宽度约 52px，中文菜单项被迫逐字换行，呈现为「竖排」文字，影响可读性与专业观感。需要在不改变现有菜单项与交互逻辑的前提下，修复收起态下的弹出层布局。

## What Changes

- 在前台 `studio.css` 与后台 `admin-studio.css` 中，为 `.app-shell.is-sidebar-collapsed` 下的用户菜单（`.sk-user-menu` / `.adm-user-menu`）增加收起态专用定位：菜单向右浮出侧栏轨道，设置合理 `min-width` 与 `white-space: nowrap`，保证菜单项横排显示。
- 展开态用户菜单布局与行为保持不变。
- 不新增 API、不修改 HTML 结构或 JavaScript 菜单开关逻辑（纯 CSS 方案 A）。

## Capabilities

### New Capabilities

- `sidebar-user-menu-popout`: 定义侧边栏收起时用户头像下拉菜单的弹出位置、最小宽度与可读性要求（前台与后台一致）。

### Modified Capabilities

（无。本项目 `openspec/specs/` 尚无与此相关的既有 capability。）

## Impact

- `app/static/studio.css` — 前台 SoulKing Studio 收起态 `.sk-user-menu` 样式
- `app/static/admin-studio.css` — 后台 SoulKing Admin 收起态 `.adm-user-menu` 样式
- 受影响页面：`app/static/index.html`、`app/static/admin.html`（仅视觉，无结构变更）
- 需手动验证：收起侧栏 → 点击头像 → 菜单文字横排、不被父级 `overflow` 裁切、z-index 高于主内容区
