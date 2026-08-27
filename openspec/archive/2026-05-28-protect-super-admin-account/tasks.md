## 1. 后端判定与 API

- [x] 1.1 在 `app/auth.py` 新增 `is_super_admin(user)`：比较 `user.username` 与 `Settings.admin_username`（大小写不敏感）
- [x] 1.2 在 `app/auth_routes.py` 的 `update_admin_user` 中，将 `role=admin` 禁用拦截改为 `is_super_admin(user)`，错误信息改为「不能禁用超级管理员账号」
- [x] 1.3 在 `AdminUserOut` 增加 `is_super_admin: bool` 字段，列表与 PATCH 响应由服务端填充

## 2. 后台 UI

- [x] 2.1 在 `app/static/admin.js` 的 `renderUsersManager` 中，将隐藏禁用按钮的条件从 `u.role === "admin"` 改为 `u.is_super_admin`

## 3. 验证

- [x] 3.1 确认 `username=admin` 超级管理员不可被 PATCH 禁用（400）
- [x] 3.2 确认其它 `role=admin` 用户可被正常禁用
- [x] 3.3 确认用户管理页仅超级管理员行无禁用按钮，其它 admin 行有

## 4. 规格归档

- [x] 4.1 实现完成后运行 `/opsx:archive` 合并 `user-administration` delta 入主 spec
