## 1. 依赖与基础模块（Phase 1 前置）

- [x] 1.1 在 `requirements.txt` 增加密码哈希依赖（`bcrypt`）
- [x] 1.2 新增 `app/auth.py`：`hash_password` / `verify_password`、`validate_password_complexity`、会话创建/删除/按 user 踢会话
- [x] 1.3 在 `app/config.py` 增加 `admin_username`、`admin_password`（可选，仅空库种子用）

## 2. 数据模型与迁移（Phase 1）

- [x] 2.1 在 `app/models.py` 增加 `User`（含 `username`、`password_hash`、`nickname`、`avatar_object_key`、`role`、`is_active`、`deleted_at`、时间戳）
- [x] 2.2 在 `app/models.py` 增加 `Session`（`id`、`user_id`、`expires_at`）
- [x] 2.3 为 `Playlist` 增加 `user_id` 外键；在 `ensure_schema` 中迁移列、将存量歌单 `user_id` 设为种子管理员、调整唯一约束为 per-user 名称
- [x] 2.4 实现空库时种子管理员创建（读环境变量，密码过复杂度校验）
- [x] 2.5 在 `app/main.py` 启动流程调用上述迁移与种子逻辑

## 3. 鉴权依赖与 Auth API（Phase 1）

- [x] 3.1 实现 `get_current_user` / `require_user` / `require_admin` FastAPI 依赖（校验 session、active、未软删）
- [x] 3.2 实现 `POST /auth/login`、`POST /auth/logout`、`GET /auth/me`（me 含 presigned `avatar_url`）
- [x] 3.3 为业务路由挂载 `require_user`；为 `/admin/*` 管理 API 挂载 `require_admin`
- [x] 3.4 登记公开路由白名单：`GET /login`、`POST /auth/login`、`GET /health`、登录静态资源
- [x] 3.5 更新所有 `/playlists*` 处理器：按 `current_user.id` 过滤与校验归属

## 4. 登录页（Phase 1）

- [x] 4.1 新增 `app/static/login.html`（及样式），`GET /login` 返回该页
- [x] 4.2 实现登录表单提交 `POST /auth/login`、成功跳转 `next` 或 `/`
- [x] 4.3 `frontend.js` / `admin.js` 的 `request()` 增加 `credentials: 'include'` 与 401 → `/login?next=...`

## 5. 前台壳 Phase 1 接线（Phase 1）

- [x] 5.1 前台壳启动时 `GET /auth/me`，未登录跳转登录页
- [x] 5.2 侧栏展示 `/auth/me` 的昵称与 `avatar_url`（无头像首字母占位）
- [x] 5.3 「进入后台」仅 `role===admin` 时渲染；非 admin 访问 `/admin` 由 API/页面返回 403 或重定向
- [x] 5.4 确认退出后调用 `POST /auth/logout` 并跳转 `/login`（替换 demo toast）
- [x] 5.5 后台壳同样：me 加载、真实展示名、登出跳转登录页

## 6. Phase 1 验证

- [x] 6.1 冒烟：无 Cookie 访问 `/songs` 返回 401；登录后可访问
- [x] 6.2 冒烟：用户 A/B 歌单列表互不可见；存量歌单在种子 admin 下可见
- [x] 6.3 冒烟：普通用户 `/admin` API 403；admin 可访问
- [x] 6.4 更新 README / `.env.example`：种子管理员环境变量与首次登录说明

## 7. 自助资料 API（Phase 2）

- [x] 7.1 实现 `PATCH /users/me`（`nickname`、`username` 唯一与格式校验）
- [x] 7.2 实现 `POST /users/me/password`（旧密码 + 新密码复杂度）
- [x] 7.3 实现 `POST /users/me/avatar`（类型/大小校验，写入 `avatar/{user_id}.{ext}`，删旧对象）

## 8. 前台自助 UI（Phase 2）

- [x] 8.1 「个人资料」模态/表单：编辑昵称、用户名，调用 `PATCH /users/me`
- [x] 8.2 「修改密码」模态：旧密码 + 新密码 + 复杂度提示，调用 `POST /users/me/password`
- [x] 8.3 个人资料内头像上传，成功后刷新 `/auth/me` 更新侧栏头像
- [x] 8.4 可选：`avatar_url` 临近过期时 focus 或定时刷新 `/auth/me`

## 9. Phase 2 验证

- [x] 9.1 管理员与普通用户均可在前台菜单改昵称、用户名、密码、头像
- [x] 9.2 用户名冲突与密码复杂度错误展示可读提示

## 10. 用户管理 API（Phase 3）

- [x] 10.1 实现 `GET /admin/users`（未软删列表）
- [x] 10.2 实现 `POST /admin/users`（创建，复杂度初始密码）
- [x] 10.3 实现 `PATCH /admin/users/{id}`（`role`、`is_active`、`nickname`；禁用时踢会话）
- [x] 10.4 实现 `DELETE /admin/users/{id}`（软删 + 踢会话；禁止删最后 admin）
- [x] 10.5 实现 `POST /admin/users/{id}/reset-password`

## 11. 后台用户管理 UI（Phase 3）

- [x] 11.1 在 `admin.html` 侧栏增加「用户管理」导航与主内容区页面骨架
- [x] 11.2 在 `admin.js` 实现列表、创建、编辑角色/启用、软删、重置密码交互
- [x] 11.3 样式与现有管理页（标签/语言）对齐

## 12. Phase 3 验证

- [x] 12.1 管理员可创建 user/admin 账号；新用户可登录
- [x] 12.2 禁用用户后立即 401；软删用户不可登录且不出现在默认列表
- [x] 12.3 无法删除最后一名 active admin

## 13. 规范合并（各 Phase 完成后或最终）

- [x] 13.1 运行 OpenSpec 归档流程，将 delta 合并入主 specs（`application-auth`、`user-self-service`、`user-administration`、`single-tenant-trust-model`、`playlist-management`、`web-static-client-shells`）
