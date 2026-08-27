## ADDED Requirements

### Requirement: 用户名密码登录

系统 SHALL 提供 `POST /auth/login`，接受用户名与密码；校验用户存在、未软删、`is_active` 为真且密码正确。成功时创建服务端会话并通过 `Set-Cookie` 下发 HttpOnly 会话 Cookie（`SameSite=Lax`，`Path=/`）。失败时返回 401，不泄露用户名是否存在以外的区分信息。

#### Scenario: 登录成功

- **GIVEN** 用户存在且已启用、未软删，密码正确
- **WHEN** 客户端提交有效用户名与密码
- **THEN** 响应表示成功
- **AND** 响应头包含会话 Cookie

#### Scenario: 密码错误

- **GIVEN** 用户存在但密码不正确
- **WHEN** 客户端提交登录请求
- **THEN** 返回 401

#### Scenario: 已禁用或已软删用户无法登录

- **GIVEN** 用户 `is_active` 为假或 `deleted_at` 非空
- **WHEN** 客户端提交登录请求
- **THEN** 返回 401

### Requirement: 登出

系统 SHALL 提供 `POST /auth/logout`；删除当前请求所对应的服务端会话记录，并清除会话 Cookie。

#### Scenario: 登出成功

- **GIVEN** 客户端携带有效会话 Cookie
- **WHEN** 客户端请求登出
- **THEN** 当前会话失效
- **AND** 后续请求不带新 Cookie 时视为未登录

### Requirement: 当前用户信息与头像 URL

系统 SHALL 提供 `GET /auth/me`；须已登录。响应包含用户标识、用户名、昵称（展示用）、角色（`admin` 或 `user`）、`is_active` 状态。若用户配置了头像对象键，响应 SHALL 包含短期有效的 `avatar_url`（对 `music-files` 桶内对象 presigned GET URL）；无头像时 `avatar_url` 为空或省略。

#### Scenario: 已登录获取 me

- **GIVEN** 客户端携带有效会话
- **WHEN** 客户端请求 `/auth/me`
- **THEN** 返回当前用户信息
- **AND** 若有头像则 `avatar_url` 可在一段时间内用于 GET 访问

#### Scenario: 未登录访问 me

- **GIVEN** 客户端无有效会话
- **WHEN** 客户端请求 `/auth/me`
- **THEN** 返回 401

### Requirement: 业务 API 须已登录

除明确公开的端点外，所有业务 HTTP API（含曲库读取、播放流、歌单、参考数据及写操作）SHALL 要求有效会话；无会话或会话无效时返回 401。

#### Scenario: 未登录访问曲库列表

- **GIVEN** 客户端未携带有效会话
- **WHEN** 客户端请求歌曲列表类 API
- **THEN** 返回 401

#### Scenario: 已登录可访问共享曲库

- **GIVEN** 普通用户（`user` 角色）已登录
- **WHEN** 客户端请求歌曲列表类 API
- **THEN** 不因角色为 `user` 而拒绝（若资源存在则按业务返回）

### Requirement: 管理端点须管理员角色

路径以 `/admin/` 为前缀的管理类 API（含扫描、批量治理、用户管理等）及返回 `admin.html` 的页面路由 SHALL 要求当前用户角色为 `admin`；已登录但非管理员返回 403。

#### Scenario: 普通用户访问管理 API

- **GIVEN** 已登录且角色为 `user`
- **WHEN** 客户端请求 `/admin/` 下任一管理 API
- **THEN** 返回 403

#### Scenario: 管理员访问管理 API

- **GIVEN** 已登录且角色为 `admin`
- **WHEN** 客户端请求管理 API 且满足业务校验
- **THEN** 不因角色原因拒绝

### Requirement: 密码复杂度

创建用户、修改密码、种子管理员初始化密码时，明文密码 MUST 同时满足：长度不少于 8；至少包含一个大写字母、一个小写字母、一个数字、一个非字母数字特殊字符。不满足时返回 400 及可读错误说明。

#### Scenario: 密码过短

- **GIVEN** 提交的新密码长度小于 8
- **WHEN** 服务端校验密码
- **THEN** 返回 400

#### Scenario: 缺少字符类别

- **GIVEN** 提交的新密码未同时包含大写、小写、数字与特殊字符
- **WHEN** 服务端校验密码
- **THEN** 返回 400

#### Scenario: 符合复杂度

- **GIVEN** 提交的新密码满足全部复杂度规则
- **WHEN** 服务端校验密码
- **THEN** 校验通过并允许持久化哈希

### Requirement: 禁用用户立即失效会话

当用户被设置为禁用（`is_active=false`）时，系统 MUST 在同一业务事务或紧接操作中删除该用户在 `sessions` 表中的全部会话记录，使既有 Cookie 立即失效。

#### Scenario: 禁用后旧 Cookie 无效

- **GIVEN** 用户曾登录且持有有效 Cookie
- **WHEN** 管理员将该用户禁用
- **THEN** 该用户随后使用旧 Cookie 请求 `/auth/me` 返回 401

### Requirement: 种子管理员

当数据库中不存在任何未软删用户时，应用启动或 `ensure_schema` 流程 SHALL 根据环境变量 `ADMIN_USERNAME` 与 `ADMIN_PASSWORD` 创建一名 `admin` 角色用户；密码须通过复杂度校验。若已存在用户则不得重复创建。

#### Scenario: 空库首次启动

- **GIVEN** `users` 表无未软删记录且环境变量已配置
- **WHEN** 应用完成 schema 确保
- **THEN** 存在一名可登录的管理员账号

### Requirement: 公开端点

下列端点 SHALL 不要求登录：`GET /login`（登录页 HTML）、`POST /auth/login`、`GET /health`，以及登录页所需的静态资源（样式、脚本、logo 等）。其余端点按本规范要求鉴权。

#### Scenario: 未登录可打开登录页

- **GIVEN** 客户端无会话
- **WHEN** 客户端请求 `GET /login`
- **THEN** 返回登录页 HTML
