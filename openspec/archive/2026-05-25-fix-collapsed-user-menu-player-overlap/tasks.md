## 1. 前台层叠修复

- [x] 1.1 在 `app/static/studio.css` 为 `.front-app .app-shell.is-sidebar-collapsed .app-sidebar`（或 `.sk-studio-sidebar`）添加 `position: relative` 与 `z-index: 55`（高于 `.studio-player` 的 50）

## 2. 后台层叠修复

- [x] 2.1 在 `app/static/admin-studio.css` 为 `.admin-app .app-shell.is-sidebar-collapsed .app-sidebar` 添加 `position: relative` 与 `z-index: 45`（高于 `#adminStudioPlayer` 的 40）

## 3. 手动验收

- [x] 3.1 前台：收起侧栏 → 打开用户菜单 → 确认菜单不被底部播放器遮挡且全部项可点击
- [x] 3.2 后台：收起侧栏 → 打开用户菜单 → 确认菜单不被底部试听条遮挡且全部项可点击
- [x] 3.3 前台/后台：展开侧栏 → 打开用户菜单 → 确认布局与层叠与变更前一致
