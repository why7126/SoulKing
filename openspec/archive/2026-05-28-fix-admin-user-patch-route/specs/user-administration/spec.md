## ADDED Requirements

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
