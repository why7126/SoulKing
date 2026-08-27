## MODIFIED Requirements

### Requirement: 更新用户

管理员 SHALL 可通过 `PATCH /admin/users/{id}` 修改昵称、角色、`is_active`；不可通过此接口修改他人用户名（他人用户名仅其本人通过 `/users/me` 修改）。当目标用户为超级管理员（`username` 与 `admin_username` 配置一致）时，不得将 `is_active` 设为 false。

#### Scenario: 禁用普通用户

- **GIVEN** 目标用户 `role=user` 且未软删
- **WHEN** 管理员将 `is_active` 设为 false
- **THEN** 该用户全部会话立即失效
- **AND** 该用户无法登录

#### Scenario: 禁用非超级管理员的管理员

- **GIVEN** 目标用户 `role=admin` 且 `username` 不等于 `admin_username`
- **WHEN** 管理员将 `is_active` 设为 false
- **THEN** 该用户全部会话立即失效
- **AND** 该用户无法登录

#### Scenario: 禁止禁用超级管理员

- **GIVEN** 目标用户 `username` 与 `admin_username` 一致且未软删
- **WHEN** 管理员将 `is_active` 设为 false
- **THEN** 返回 400
- **AND** 用户保持启用状态

#### Scenario: 提升为管理员

- **GIVEN** 目标用户角色为 `user`
- **WHEN** 管理员将其角色设为 `admin`
- **THEN** 该用户可访问管理端点

### Requirement: 禁止禁用管理员账号

系统 SHALL NOT 允许通过 `PATCH /admin/users/{id}` 将超级管理员（`username` 与 `admin_username` 配置一致）设为 `is_active=false`。若需阻止某普通管理员登录，可直接禁用；超级管理员账号为系统种子账号，不得禁用。

#### Scenario: API 拒绝禁用超级管理员

- **GIVEN** 目标用户 `username=admin_username` 且未软删
- **WHEN** 管理员 PATCH 请求将 `is_active` 设为 false
- **THEN** 返回 400
- **AND** 响应说明不能禁用超级管理员账号
- **AND** 用户 `is_active` 保持不变

#### Scenario: 允许禁用其它管理员

- **GIVEN** 目标用户 `role=admin` 且 `username` 不等于 `admin_username`
- **WHEN** 管理员 PATCH 请求将 `is_active` 设为 false
- **THEN** 返回 200
- **AND** 用户 `is_active=false`

#### Scenario: 后台仅对超级管理员隐藏禁用操作

- **GIVEN** 管理员已登录后台用户管理页
- **WHEN** 列表中存在 `username=admin_username` 的用户
- **THEN** 该行不展示「禁用/启用」切换按钮
- **AND** 其它用户（含 `role=admin` 的非超级管理员）仍展示禁用操作
