## Context

用户认证系统已上线后台用户管理。当前 `PATCH /admin/users/{id}` 允许将任意用户（含 `role=admin`）的 `is_active` 设为 `false`；禁用时会调用 `revoke_all_sessions_for_user` 立即踢掉会话。现有防护仅覆盖「不能删除/降权最后一名管理员」，未覆盖「禁用管理员账号」。

生产库中种子管理员（`id=1`, `username=admin`）当前 `is_active=0`，导致无法登录后台。`seed_admin_user` 在已有用户时仅返回第一个 admin，不会修复被禁用的状态。

## Goals / Non-Goals

**Goals:**

- 恢复当前被禁用的种子管理员，使其可立即登录
- API 层拒绝禁用 `role=admin` 的用户
- 启动时自动确保种子管理员（`username` 匹配 `Settings.admin_username`）处于启用状态
- 后台用户管理 UI 对 admin 用户不展示禁用操作

**Non-Goals:**

- 不改变普通用户（`role=user`）的禁用/启用流程
- 不禁止对 admin 用户降权（已有「最后一名管理员」保护）
- 不禁止对 admin 用户软删除（已有「最后一名管理员」保护）
- 不引入新的管理员角色或权限模型

## Decisions

### 1. 保护范围：`role=admin` 而非仅种子 username

**选择**：凡 `role=admin` 的用户均不可被设为 `is_active=false`。

**理由**：禁用 admin 与降权效果类似（均无法访问管理端），但 UI 上「禁用」按钮更易误点；统一按角色拦截语义清晰。若需封锁某管理员，应先将其降为 `user` 再禁用。

**备选**：仅保护 `username == settings.admin_username`。范围过窄，其他 admin 账号仍可能被误禁用。

### 2. 启动自愈：仅修复种子管理员

**选择**：在 `seed_admin_user` 中，当库中已有用户时，查找 `username` 与 `admin_username` 配置一致且未软删的用户；若存在且 `is_active=false`，设为 `true` 并 commit。

**理由**：针对「种子账号被锁」这一运维场景提供自动恢复，不影响其他被故意禁用的普通用户。非种子 admin 若被禁用（历史数据）不在启动时自动恢复——需管理员通过 SQL 或后续人工处理；但 API 防护可阻止再次发生。

### 3. 一次性数据修复

**选择**：实现阶段执行 `UPDATE users SET is_active=1 WHERE username='admin' AND deleted_at IS NULL`（或读取 `.env` 中 `ADMIN_USERNAME`）。

**理由**：立即解除当前锁死状态，与代码变更一并交付。

### 4. API 错误响应

**选择**：`400`，`detail="不能禁用管理员账号"`（与现有「不能删除最后一名管理员」等中文错误风格一致）。

### 5. 后台 UI

**选择**：`renderUsersManager` 中，当 `u.role === "admin"` 时不渲染「禁用/启用」按钮；admin 用户状态列仍显示「启用」。

**理由**：前后端双重防护；UI 层减少误操作，API 层保证安全。

## Risks / Trade-offs

- **[历史数据]** 若存在多名 `role=admin` 且 `is_active=false` 的记录，仅种子账号在启动时自愈 → 实现任务中可选手动 SQL 检查；API 防护防止新增
- **[降权后禁用]** 管理员须先降权再禁用，多一步操作 → 符合最小权限原则，可接受
- **[直接改库绕过 API]** 运维仍可通过 SQL 禁用 admin → 启动自愈可修复种子账号；非种子需文档说明

## Migration Plan

1. 部署前或部署时执行 SQL 恢复种子 admin
2. 发布含 API/UI/启动逻辑的新代码
3. 验证：以 admin 登录后台 → 用户管理页 admin 行无禁用按钮 → 直接调 API 尝试禁用 admin 返回 400
4. 回滚：还原代码；数据侧 admin 已恢复，回滚不会重新禁用

## Open Questions

（无）
