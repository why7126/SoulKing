## 1. 修复路由

- [x] 1.1 在 `app/auth_routes.py` 的 `update_admin_user` 前补回 `@router.patch("/admin/users/{user_id}", response_model=AdminUserOut)` 装饰器
- [x] 1.2 确认 `create_admin_user` 与 `update_admin_user` 之间有正确空行，代码格式正常

## 2. HTTP 验证

- [x] 2.1 通过 HTTP `PATCH /admin/users/{id}` 禁用非超级管理员用户，确认返回 200（非 405）
- [x] 2.2 通过 HTTP `PATCH /admin/users/{id}` 修改角色，确认返回 200
- [x] 2.3 通过 HTTP `PATCH /admin/users/{admin_id}` 尝试禁用超级管理员，确认返回 400

## 3. 规格归档

- [x] 3.1 实现完成后运行 `/opsx:archive` 合并 `user-administration` delta 入主 spec
