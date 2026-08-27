## Why

`align-collapsed-user-menu-item-avatar` 已将收起侧栏时的用户菜单改为左对齐头像上方弹出，但当前 CSS 在 `bottom` 计算中额外叠加了 `--sk-player-total-h` / `--adm-player-total-h`，导致菜单与头像之间的垂直间距远大于展开侧栏时的 `6px` 固定间隙。视觉上菜单「飘」在头像上方过远，与展开态不一致，影响交互预期与精致感。

## What Changes

- 将 `studio.css` / `admin-studio.css` 中收起态用户菜单的 `bottom` 从 `calc(100% + var(--*-player-total-h) + 6px)` 改为与展开态一致的 `calc(100% + 6px)`。
- 保留收起态已有的左对齐头像、`min-width`、`white-space: nowrap` 等规则，不恢复向右浮出。
- 展开侧栏时用户菜单布局与行为保持不变。
- 不新增 API、不修改 HTML 结构或 JavaScript 菜单开关逻辑（纯 CSS 调整）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `sidebar-user-menu-popout`：补充收起侧栏时用户菜单与头像之间的垂直间隙 MUST 与展开侧栏时一致（均为 `6px`）的要求及验收场景。

## Impact

- `app/static/studio.css` — 前台收起态 `.sk-user-menu` 的 `bottom` 定位
- `app/static/admin-studio.css` — 后台收起态 `.adm-user-menu` 的 `bottom` 定位
- 受影响页面：`app/static/index.html`、`app/static/admin.html`（仅视觉间距，无结构变更）
- 需手动验证：收起/展开侧栏分别打开用户菜单，对比菜单底边与头像顶边的垂直间距一致
