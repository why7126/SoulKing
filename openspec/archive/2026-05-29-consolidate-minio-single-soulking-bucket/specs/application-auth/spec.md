## MODIFIED Requirements

### Requirement: 当前用户信息与头像 URL

系统 SHALL 提供 `GET /auth/me`；须已登录。响应包含用户标识、用户名、昵称（展示用）、角色（`admin` 或 `user`）、`is_active` 状态。若用户配置了头像对象键，响应 SHALL 包含短期有效的 `avatar_url`（对 `soulking` 桶内对象 presigned GET URL）；无头像时 `avatar_url` 为空或省略。客户端展示头像时 MUST 原样使用该 URL，不得在未重新签发的情况下追加或修改查询参数。

#### Scenario: 已登录获取 me

- **GIVEN** 客户端携带有效会话
- **WHEN** 客户端请求 `/auth/me`
- **THEN** 返回当前用户信息
- **AND** 若有头像则 `avatar_url` 可在一段时间内用于 GET 访问

#### Scenario: 未登录访问 me

- **GIVEN** 客户端无有效会话
- **WHEN** 客户端请求 `/auth/me`
- **THEN** 返回 401
