## 1. 前台 CSS 修改

- [x] 1.1 在 `app/static/studio.css` 中，将 `.front-app .app-shell.is-sidebar-collapsed .sk-user-menu` 的 `left: calc(100% + 8px)` 替换为 `left: calc(50% - 18px)`，保留 `right: auto`、`width: max-content`、`min-width: 160px`
- [x] 1.2 确认收起态 `.sk-user-menu-item` 的 `white-space: nowrap` 规则仍存在

## 2. 后台 CSS 修改

- [x] 2.1 在 `app/static/admin-studio.css` 中，将 `.admin-app .app-shell.is-sidebar-collapsed .adm-user-menu` 的 `left: calc(100% + 8px)` 替换为 `left: calc(50% - 18px)`，保留 `right: auto`、`width: max-content`、`min-width: 160px`
- [x] 2.2 确认收起态 `.adm-user-menu-item` 的 `white-space: nowrap` 规则仍存在

## 3. 手动验收

- [x] 3.1 前台：收起侧栏 → 点击用户头像 → 菜单在头像上方、左缘对齐头像、文案横排、不被底部播放器遮挡、全部菜单项可点击
- [x] 3.2 后台：收起侧栏 → 点击用户头像 → 菜单在头像上方、左缘对齐头像、文案横排、不被试听条遮挡、全部菜单项可点击
- [x] 3.3 前台与后台：展开侧栏 → 打开用户菜单 → 布局与变更前一致
- [x] 3.4 确认 `frontend.js` 与 `admin.js` 无菜单定位相关改动
