## 1. 数据恢复

- [x] 1.1 执行 SQL 将种子管理员（`username` 与 `ADMIN_USERNAME` 一致，默认 `admin`）的 `is_active` 设为 `true`
- [x] 1.2 确认 `users` 表中该记录 `deleted_at` 为空且可正常登录后台

## 2. 后端 API 与启动逻辑

- [x] 2.1 在 `app/auth_routes.py` 的 `update_admin_user` 中，当目标用户 `role=admin` 且 `payload.is_active is False` 时返回 400（`不能禁用管理员账号`）
- [x] 2.2 在 `app/auth.py` 的 `seed_admin_user` 中，当库中已有用户时查找 `username == settings.admin_username` 的用户；若存在且 `is_active=false`，自动设为 `true` 并 commit

## 3. 后台 UI

- [x] 3.1 在 `app/static/admin.js` 的 `renderUsersManager` 中，对 `role=admin` 的用户不渲染「禁用/启用」按钮

## 4. 验证

- [x] 4.1 以 admin 账号登录后台，确认用户管理页 admin 行无禁用按钮
- [x] 4.2 直接调用 `PATCH /admin/users/{admin_id}` 尝试 `is_active=false`，确认返回 400
- [x] 4.3 重启应用后确认种子 admin 仍为启用状态

## 5. 规格归档

- [x] 5.1 实现完成后运行 `/opsx:archive` 将 `user-administration` delta 合并入主 spec
