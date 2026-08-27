## Why

种子管理员账号（`username=admin`）已在后台被误设为禁用（`is_active=false`），导致无法登录管理端，系统陷入无可用管理员的状态。当前用户管理 API 与后台界面仅保护「最后一名管理员」不被删除或降权，却未禁止对管理员账号执行禁用操作，存在同类风险再次发生。

## What Changes

- **数据恢复**：将当前被禁用的种子管理员账号（`username` 与 `ADMIN_USERNAME` 配置一致，默认 `admin`）恢复为 `is_active=true`，并清除其无效会话以便重新登录。
- **API 防护**：`PATCH /admin/users/{id}` 当目标用户 `role=admin` 时，拒绝将 `is_active` 设为 `false`，返回 400 及明确错误信息。
- **启动自愈**：应用启动时 `seed_admin_user` 除创建首用户外，若种子管理员存在但被禁用，自动将其恢复为启用状态，防止部署后长期锁死。
- **后台 UI**：用户管理列表中，对 `role=admin` 的用户隐藏或禁用「禁用/启用」切换按钮，避免误操作。
- **规格更新**：在 `user-administration` 中补充「禁止禁用管理员账号」及恢复场景。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `user-administration`：禁止通过 PATCH 将 `role=admin` 的用户设为禁用；补充种子管理员恢复与后台 UI 约束。

## Impact

- `data/music.db` — 一次性恢复种子管理员 `is_active`
- `app/auth.py` — `seed_admin_user` 启动时确保种子管理员启用
- `app/auth_routes.py` — `update_admin_user` 拒绝禁用 admin 角色用户
- `app/static/admin.js` — 用户管理页对 admin 用户隐藏禁用操作
- `openspec/specs/user-administration/spec.md` — 主 spec 合并 delta
