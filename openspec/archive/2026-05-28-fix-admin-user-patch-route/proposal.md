## Why

后台用户管理点击「禁用/启用」或「角色」时，前端调用 `PATCH /admin/users/{id}`，但服务端 `update_admin_user` 在 `protect-super-admin-account` 重构中意外丢失了 `@router.patch` 装饰器，函数未注册为 HTTP 路由。FastAPI 在同路径存在 `DELETE /admin/users/{id}` 时，对 PATCH 请求返回 **405 Method Not Allowed**，导致禁用、启用、改角色均失败。

## What Changes

- **恢复路由注册**：为 `app/auth_routes.py` 中 `update_admin_user` 补回 `@router.patch("/admin/users/{user_id}", response_model=AdminUserOut)` 装饰器。
- **HTTP 层验证**：补充针对 `PATCH /admin/users/{id}` 的集成验证（禁用普通用户、禁止禁用超级管理员、改角色），避免仅测 Python 直调而漏掉路由问题。
- **规格补充**：在 `user-administration` 中明确 PATCH 端点须正常响应（非 405），作为回归验收场景。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `user-administration`：补充 PATCH 端点 HTTP 可达性验收场景（回归防护）。

## Impact

- `app/auth_routes.py` — 恢复 `@router.patch` 装饰器（一行）
- 测试或验证脚本 — PATCH 端点 HTTP 行为
- `openspec/specs/user-administration/spec.md` — 合并回归场景 delta
