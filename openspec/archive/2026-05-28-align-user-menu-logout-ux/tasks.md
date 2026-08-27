## 1. HTML 与 class

- [x] 1.1 在 `app/static/index.html` 为 `#frontUserLogoutBtn` 增加 `user-menu-item--destructive` class（保留 `sk-user-menu-item`）
- [x] 1.2 在 `app/static/admin.html` 为 `#logoutBtn` 增加 `user-menu-item--destructive` class（保留 `adm-user-menu-item`）

## 2. 样式（前台 + 后台）

- [x] 2.1 在 `app/static/studio.css` 新增 `.user-menu-item--destructive` 规则（`color: var(--sk-danger)`、hover 淡红背景、顶部分隔线与间距）
- [x] 2.2 在 `app/static/admin-studio.css` 新增对称的 `.user-menu-item--destructive` 规则（`--adm-danger`）
- [x] 2.3 删除 `admin-studio.css` 中 `.adm-user-menu-item:last-child` 及其 `:hover` 规则

## 3. 退出确认交互

- [x] 3.1 在 `app/static/frontend.js` 实现 `confirmLogout()`：关菜单 → `openModal` 确认 → 确认后 toast；`#frontUserLogoutBtn` 经 `handleFrontUserMenuItem` 调用
- [x] 3.2 在 `app/static/admin.js` 实现对称 `confirmLogout()`；`#logoutBtn` 点击时关菜单并走确认流程（替换直接 toast）

## 4. 验收

- [x] 4.1 前台：展开/收起侧栏下打开用户菜单，确认「退出登录」危险色、与「进入后台」分隔、确认/取消流程
- [x] 4.2 后台：同上，确认与前台视觉与交互一致
- [x] 4.3 确认未改动 `sidebar-user-menu-popout` 相关定位规则
