## Why

上一变更 `protect-admin-account` 将保护范围扩大到了所有 `role=admin` 的用户，导致其它管理员账号也无法在后台被禁用，与产品预期不符。实际需保护的是**用户名为 `admin`（与 `ADMIN_USERNAME` 配置一致）的种子超级管理员账号**，而非整个管理员角色；其它 `role=admin` 的用户仍应允许正常禁用。

## What Changes

- **收窄 API 防护**：`PATCH /admin/users/{id}` 仅当目标用户 `username` 与 `Settings.admin_username` 一致（大小写不敏感）时，拒绝将 `is_active` 设为 `false`；其它 admin 角色用户可正常禁用。
- **提取公共判定**：在 `app/auth.py` 新增 `is_super_admin(user)` 辅助函数，统一后端「超级管理员」判定逻辑（基于 `admin_username` 配置，非 `role`）。
- **后台 UI 收窄**：用户管理列表仅对超级管理员账号（`username=admin_username`）隐藏「禁用/启用」按钮；其它管理员行恢复禁用操作。
- **规格修订**：更新 `user-administration` 中「禁止禁用管理员账号」相关需求，将保护对象从 `role=admin` 改为种子超级管理员（`username=admin_username`）；启动自愈逻辑保持不变。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `user-administration`：禁止禁用的对象从「所有 admin 角色用户」收窄为「username 与 `admin_username` 一致的超级管理员」；后台 UI 与 API 行为一致。

## Impact

- `app/auth.py` — 新增 `is_super_admin()`；`seed_admin_user` 逻辑不变（已基于 `admin_username`）
- `app/auth_routes.py` — `update_admin_user` 改用 `is_super_admin()` 替代 `role=admin` 判断
- `app/static/admin.js` — 禁用按钮隐藏条件改为超级管理员 username，非 admin 角色
- `openspec/specs/user-administration/spec.md` — 主 spec 合并 delta，替换过宽的角色级保护描述
