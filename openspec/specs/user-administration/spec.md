# user-administration Specification

## Purpose

定义管理员在后台对用户账号进行全生命周期管理的能力：创建、列表、更新角色与启用状态、软删除与重置密码；不开放自助注册。
## Requirements
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

### Requirement: 种子管理员启动自愈

应用启动时，若存在 `username` 与配置的 `admin_username` 一致、未软删、但 `is_active=false` 的用户，系统 SHALL 自动将其设为 `is_active=true`，以确保种子管理员可登录。

#### Scenario: 启动恢复被禁用的种子 admin

- **GIVEN** 库中存在 `username=admin_username` 且 `is_active=false`、`deleted_at` 为空
- **WHEN** 应用完成启动初始化（`seed_admin_user`）
- **THEN** 该用户 `is_active=true`
- **AND** 可使用密码登录管理端

### Requirement: PATCH 用户端点 HTTP 可达

`PATCH /admin/users/{id}` SHALL 作为已注册的 HTTP 路由对外提供服务；对合法管理员会话的请求 MUST NOT 返回 405 Method Not Allowed。

#### Scenario: PATCH 禁用用户返回 200

- **GIVEN** 管理员已登录且目标用户为可禁用的非超级管理员
- **WHEN** 发送 HTTP `PATCH /admin/users/{id}`，`body: { "is_active": false }`
- **THEN** 响应状态码为 200（非 405）
- **AND** 用户 `is_active=false`

#### Scenario: PATCH 修改角色返回 200

- **GIVEN** 管理员已登录且目标用户存在
- **WHEN** 发送 HTTP `PATCH /admin/users/{id}`，`body: { "role": "admin" }`
- **THEN** 响应状态码为 200（非 405）
- **AND** 用户角色已更新

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

后台壳 SHALL 提供「用户管理」导航页，支持列表展示、创建用户、编辑角色与启用状态、软删除、重置密码；页面布局、工具栏、搜索框、表格与底栏视觉 MUST 与后台「歌曲管理」及统一后的艺人/标签/语言管理页采用同一 SoulKing Admin 组件体系（`admin-studio-root`、`adm-toolbar`、`adm-search-wrap`、`adm-data-table` 或等价 Admin 表样式、`adm-table-footer`），不得继续以 Hermes `panel` + `admin-search-row` 作为主结构。列表操作列 MUST 仅展示「更多」（⋮）按钮，切换角色、启用/禁用、重置密码、删除 MUST 位于 `.table-more-menu` 内，不得行内并列多按钮。

#### Scenario: 管理员打开用户管理页

- **GIVEN** 管理员已登录后台壳
- **WHEN** 用户点击侧栏「用户管理」
- **THEN** 主内容区展示用户列表与操作入口
- **AND** 页面呈现与「歌曲管理」一致的 Admin 工具栏与表格容器结构

#### Scenario: 用户管理操作列仅更多按钮

- **GIVEN** 用户管理列表已加载
- **WHEN** 用户查看任意用户行的操作列
- **THEN** 可见控件仅为「更多」（⋮）按钮
- **AND** 行内不存在独立的「角色」「重置密码」「删除」按钮

