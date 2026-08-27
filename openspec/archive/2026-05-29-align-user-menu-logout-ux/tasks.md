## 1. 前台 Studio 退出确认弹层

- [x] 1.1 在 `app/static/index.html` 新增 `#logoutConfirmOverlay`（`sk-self-service-overlay` + `sk-modal-card`：标题、说明、取消、危险确认按钮）
- [x] 1.2 在 `app/static/studio.css` 新增 `btn-studio-danger`（或等价）映射 `--sk-danger` 与 hover 语义
- [x] 1.3 在 `app/static/frontend.js` 将 `confirmLogout()` 改为显示/隐藏专用 overlay（遮罩、Esc、关闭按钮取消）；确认后保留 `POST /auth/logout` + `/login`；移除对 `openModal` 的调用

## 2. 后台 Admin 退出确认弹层

- [x] 2.1 在 `app/static/admin.html` 新增对称 `#logoutConfirmOverlay`（Admin 皮肤 class）
- [x] 2.2 在 `app/static/admin-studio.css` 新增 `adm-self-service-overlay` / `adm-modal-card`（若尚无）与 `btn-adm-danger`
- [x] 2.3 在 `app/static/admin.js` 对称改造 `confirmLogout()`，不再调用 `openModal`

## 3. 用户菜单样式回归

- [x] 3.1 确认前后台「退出登录」仍带 `user-menu-item--destructive` 与顶部分隔（`studio.css` / `admin-studio.css`）
- [x] 3.2 确认 `admin-studio.css` 无 `.adm-user-menu-item:last-child` 危险色规则

## 4. 文档与验收

- [x] 4.1 更新 `ui-design.md`：退出确认已使用 Studio/Admin 专用弹层（非 Hermes `#modalOverlay`）
- [x] 4.2 前台：展开/收起侧栏 → 用户菜单危险项与分隔 → Studio 确认弹层 → 取消/确认登出
- [x] 4.3 后台：同上，确认 Admin 弹层与前台交互对称
- [x] 4.4 确认未改动 `sidebar-user-menu-popout` 定位规则
