## 1. CSS 调整

- [x] 1.1 在 `app/static/studio.css` 中，将 `.front-app .app-shell.is-sidebar-collapsed .sk-user-menu` 的 `bottom` 从 `calc(100% + var(--sk-player-total-h) + 6px)` 改为 `calc(100% + 6px)`
- [x] 1.2 在 `app/static/admin-studio.css` 中，将 `.admin-app .app-shell.is-sidebar-collapsed .adm-user-menu` 的 `bottom` 从 `calc(100% + var(--adm-player-total-h) + 6px)` 改为 `calc(100% + 6px)`

## 2. 验收

- [x] 2.1 前台：展开侧栏 → 打开用户菜单 → 确认菜单与头像间距为 6px（DevTools 测量或目测）
- [x] 2.2 前台：收起侧栏 → 打开用户菜单 → 确认间距与展开态一致，菜单仍左对齐头像、文字横排
- [x] 2.3 后台：重复 2.1–2.2 的展开/收起对比验收
- [x] 2.4 确认 `frontend.js` / `admin.js` 无菜单定位相关改动（纯 CSS 变更）
