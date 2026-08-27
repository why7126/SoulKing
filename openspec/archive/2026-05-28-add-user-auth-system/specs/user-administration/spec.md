## ADDED Requirements

### Requirement: 仅管理员可管理用户

用户管理 API（`GET/POST/PATCH/DELETE /admin/users` 及重置密码等子资源）SHALL 要求当前会话用户角色为 `admin`。非管理员返回 403。

#### Scenario: 普通用户访问用户管理 API

- **GIVEN** 已登录角色为 `user`
- **WHEN** 请求 `/admin/users`
- **THEN** 返回 403

### Requirement: 列出用户

管理员 SHALL 可获取未软删用户列表；每条包含标识、用户名、昵称、角色、`is_active`、创建时间等摘要字段；默认不包含已软删用户。

#### Scenario: 管理员列出用户

- **GIVEN** 管理员已登录
- **WHEN** 请求用户列表
- **THEN** 返回所有未软删用户

### Requirement: 创建用户

管理员 SHALL 可通过 `POST /admin/users` 创建账号，提交用户名、初始密码、可选昵称、角色（`admin` 或 `user`）；用户名唯一；初始密码须满足复杂度。系统不开放自助注册。

#### Scenario: 创建普通用户

- **GIVEN** 管理员已登录且用户名未被占用
- **WHEN** 提交创建请求
- **THEN** 新用户可凭用户名与初始密码登录

#### Scenario: 用户名已存在

- **GIVEN** 未软删用户已占用该用户名
- **WHEN** 管理员尝试创建同用户名
- **THEN** 返回 400

### Requirement: 更新用户

管理员 SHALL 可通过 `PATCH /admin/users/{id}` 修改昵称、角色、`is_active`；不可通过此接口修改他人用户名（他人用户名仅其本人通过 `/users/me` 修改）。

#### Scenario: 禁用用户

- **GIVEN** 目标用户存在且未软删
- **WHEN** 管理员将 `is_active` 设为 false
- **THEN** 该用户全部会话立即失效
- **AND** 该用户无法登录

#### Scenario: 提升为管理员

- **GIVEN** 目标用户角色为 `user`
- **WHEN** 管理员将其角色设为 `admin`
- **THEN** 该用户可访问管理端点

### Requirement: 软删除用户

管理员 SHALL 可通过 `DELETE /admin/users/{id}` 软删除用户：设置 `deleted_at`，删除其全部会话，且该用户不可再登录。不得软删除最后一名未软删的 `admin` 用户。

#### Scenario: 软删除成功

- **GIVEN** 目标用户非最后一名 active admin
- **WHEN** 管理员删除用户
- **THEN** `deleted_at` 非空
- **AND** 用户不再出现在默认列表

#### Scenario: 禁止删除最后管理员

- **GIVEN** 库中仅一名未软删 admin
- **WHEN** 管理员尝试删除该用户
- **THEN** 返回 400 或 409

### Requirement: 重置他人密码

管理员 SHALL 可通过 `POST /admin/users/{id}/reset-password` 为目标用户设置新密码；新密码须满足复杂度要求。

#### Scenario: 重置密码后可用新密码登录

- **GIVEN** 目标用户未软删
- **WHEN** 管理员提交符合复杂度的新密码
- **THEN** 目标用户可使用新密码登录

### Requirement: 后台用户管理界面

后台壳 SHALL 提供「用户管理」导航页，支持列表展示、创建用户、编辑角色与启用状态、软删除、重置密码；交互风格与现有标签/语言管理页一致。

#### Scenario: 管理员打开用户管理页

- **GIVEN** 管理员已登录后台壳
- **WHEN** 用户点击侧栏「用户管理」
- **THEN** 主内容区展示用户列表与操作入口
