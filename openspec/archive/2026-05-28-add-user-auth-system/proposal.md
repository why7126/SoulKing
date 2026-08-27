## Why

当前系统在应用层不对 HTTP 请求做身份鉴别，任何人可访问曲库 API 与 `/admin` 管理端，与产品向「多账号、分角色」演进的需要不符。侧栏用户菜单仅有占位交互，无法支撑真实登录、登出与个人设置。需要在保持**单部署、共享曲库**的前提下，引入基于用户名的账号体系、会话鉴权、角色门禁，并将歌单归属到各用户，同时由管理员集中开户。

## What Changes

- **BREAKING**：除公开端点（如 `/login`、`/health`、登录相关 API）外，业务 API 须已登录会话；未登录返回 401。
- **BREAKING**：`/admin` 页面及其管理类 API 仅 `admin` 角色可访问；普通用户 403。
- 新增登录页（`/login`），用户名 + 密码登录；不开放自助注册。
- 新增 `User` 数据模型与会话（HttpOnly Cookie + 服务端 `Session` 表）；首装通过环境变量种子管理员。
- 歌单表增加 `user_id`；列表/创建/重命名/删除/排序/条目操作均限定当前用户；**存量歌单迁移至种子管理员**（方案 1）。
- 曲库（`Song` 等）保持共享，不按用户分区。
- 前台用户菜单接入：个人资料（昵称、头像、**可改用户名**）、修改密码（复杂度策略）、进入后台（仅 admin）、真实登出。
- 头像存储于 `music-files` 桶 `avatar/` 前缀；`GET /auth/me` 返回短期 presigned URL 供展示。
- 禁用用户时**立即失效**其全部会话；删除用户为**软删除**（`deleted_at`）。
- 后台新增「用户管理」：增删改查、角色、启用/禁用；账号仅管理员创建。
- 密码须满足复杂度要求；管理员亦通过**前台**用户菜单修改自己的密码与头像。

实现按 **Phase 1（身份 + 歌单归属 + 门禁）→ Phase 2（自助资料）→ Phase 3（后台用户管理）** 分阶段交付，详见 `design.md` 与 `tasks.md`。

## Capabilities

### New Capabilities

- `application-auth`：登录/登出、`/auth/me`、会话、角色、`/admin` 门禁、种子管理员、密码复杂度校验、禁用即踢会话、API 鉴权依赖。
- `user-self-service`：当前用户修改昵称、用户名、头像（S3 `avatar/`）、修改密码；presigned 头像 URL。
- `user-administration`：管理员用户 CRUD、角色与启用状态、软删除、初始密码下发；不开放注册。

### Modified Capabilities

- `single-tenant-trust-model`：保留单库/无租户分区；**移除**「入站无应用层身份鉴别」与「admin 与前台同一信任平面」等条款，改为「单租户多账号 + 共享曲库」。
- `playlist-management`：歌单归属用户；名称冲突范围为**同一用户内**；鉴权与越权拒绝。
- `web-static-client-shells`：登录页、未登录重定向、侧栏展示真实用户信息与头像、菜单项行为（真实登出/资料/密码/进入后台）、401 处理。

## Impact

- `app/models.py`：`User`、`Session`；`Playlist.user_id`；软删除字段
- `app/main.py`：鉴权依赖、auth/users/admin-users 路由；`ensure_schema` 迁移与种子管理员、存量歌单归属
- `app/auth.py`（或等价模块）：密码哈希、复杂度、会话
- `app/storage.py` / 上传：头像 object key `avatar/{user_id}.{ext}`
- `app/static/login.html`、`login.css`、`login.js`（或内联脚本）
- `app/static/frontend.js`、`index.html`：会话、`/auth/me`、菜单接线
- `app/static/admin.html`、`admin.js`：门禁、用户管理页
- `app/config.py`：可选 `ADMIN_USERNAME`、`ADMIN_PASSWORD` 等
- `openspec/specs/single-tenant-trust-model/spec.md`、`playlist-management/spec.md`、`web-static-client-shells/spec.md`（经本变更 delta 合并）
- 依赖：密码哈希库（如 `passlib[bcrypt]` 或 `argon2-cffi`）
- **破坏性**：现有脚本/集成测试须带登录会话或测试账号；本地开发文档须说明种子管理员与环境变量
