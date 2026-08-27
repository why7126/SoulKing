## ADDED Requirements

### Requirement: 禁止禁用管理员账号

管理员 SHALL NOT 通过 `PATCH /admin/users/{id}` 将 `role=admin` 的用户设为 `is_active=false`。若需阻止某管理员登录，须先将其角色降为 `user`，再执行禁用。

#### Scenario: API 拒绝禁用 admin 用户

- **GIVEN** 目标用户 `role=admin` 且未软删
- **WHEN** 管理员 PATCH 请求将 `is_active` 设为 false
- **THEN** 返回 400
- **AND** 响应说明不能禁用管理员账号
- **AND** 用户 `is_active` 保持不变

#### Scenario: 后台不展示 admin 禁用操作

- **GIVEN** 管理员已登录后台用户管理页
- **WHEN** 列表中存在 `role=admin` 的用户
- **THEN** 该行不展示「禁用/启用」切换按钮
- **AND** 仍展示角色、重置密码等其它允许的操作

### Requirement: 种子管理员启动自愈

应用启动时，若存在 `username` 与配置的 `admin_username` 一致、未软删、但 `is_active=false` 的用户，系统 SHALL 自动将其设为 `is_active=true`，以确保种子管理员可登录。

#### Scenario: 启动恢复被禁用的种子 admin

- **GIVEN** 库中存在 `username=admin_username` 且 `is_active=false`、`deleted_at` 为空
- **WHEN** 应用完成启动初始化（`seed_admin_user`）
- **THEN** 该用户 `is_active=true`
- **AND** 可使用密码登录管理端

## MODIFIED Requirements

### Requirement: 更新用户

管理员 SHALL 可通过 `PATCH /admin/users/{id}` 修改昵称、角色、`is_active`；不可通过此接口修改他人用户名（他人用户名仅其本人通过 `/users/me` 修改）。当目标用户 `role=admin` 时，不得将 `is_active` 设为 false。

#### Scenario: 禁用普通用户

- **GIVEN** 目标用户 `role=user` 且未软删
- **WHEN** 管理员将 `is_active` 设为 false
- **THEN** 该用户全部会话立即失效
- **AND** 该用户无法登录

#### Scenario: 禁止禁用管理员

- **GIVEN** 目标用户 `role=admin` 且未软删
- **WHEN** 管理员将 `is_active` 设为 false
- **THEN** 返回 400
- **AND** 用户保持启用状态

#### Scenario: 提升为管理员

- **GIVEN** 目标用户角色为 `user`
- **WHEN** 管理员将其角色设为 `admin`
- **THEN** 该用户可访问管理端点
