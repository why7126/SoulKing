## Why

此前 `fix-collapsed-user-menu-popout` 采用方案 A：收起侧栏时将用户菜单向右浮出 64px 轨道（`left: calc(100% + 8px)`），虽解决了中文菜单项逐字竖排的问题，但菜单水平伸出至主内容区底部，与固定定位的播放器（`z-index: 50`）在视口上重叠，导致菜单项被遮挡、难以点击。提升 z-index 只是权宜之计。现改为更自然的交互：收起侧栏时菜单不向右浮出，而是在头像上方弹出且左边缘与头像左边缘对齐，从布局上避开播放器区域。

## What Changes

- 撤销 `studio.css` / `admin-studio.css` 中收起态 `left: calc(100% + 8px)` 的向右浮出规则。
- 新增收起态专用定位：菜单在头像行上方弹出（`bottom: calc(100% + 6px)` 保持不变），左边缘与用户头像左边缘对齐（`left` 锚定头像、`right: auto`），设置 `min-width` 与 `white-space: nowrap` 保证横排可读。
- 展开态用户菜单布局与行为保持不变。
- 不新增 API、不修改 HTML 结构或 JavaScript 菜单开关逻辑（纯 CSS 方案）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `sidebar-user-menu-popout`：将「收起侧栏时向右浮出轨道」改为「收起侧栏时左对齐用户头像上方弹出」；移除「显示在底部播放器之上」的 z-index 层叠要求（新布局从空间上避免重叠，不再依赖提升 z-index）。

## Impact

- `app/static/studio.css` — 前台收起态 `.sk-user-menu` 定位规则
- `app/static/admin-studio.css` — 后台收起态 `.adm-user-menu` 定位规则
- 受影响页面：`app/static/index.html`、`app/static/admin.html`（仅视觉，无结构变更）
- 需手动验证：收起侧栏 → 点击头像 → 菜单左对齐头像、文字横排、不被播放器遮挡
