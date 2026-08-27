## Context

- 现状：`single-tenant-trust-model` 约定应用层无入站鉴权；`Playlist` 无 `user_id` 且名称全局唯一；前台/后台用户菜单为占位（硬编码 SoulKing/Admin，登出为 demo toast）。
- 产品决策：**共享曲库**、**歌单按用户**、**仅管理员创建账号**、**用户名登录**、头像存 `music-files` 桶 `avatar/`、`/auth/me` 返回 presigned URL、存量歌单归种子管理员、密码复杂度、禁用即踢会话、用户软删、**管理员可改自己的 username**。
- 约束：FastAPI + SQLAlchemy + 静态 HTML/JS 壳；无 Alembic，依赖 `ensure_schema` 增量迁移；与现有 `S3Storage`（`s3_bucket_music`）复用。

## Goals / Non-Goals

**Goals:**

- Phase 1：可登录/登出、会话鉴权、角色门禁、`Playlist.user_id` 与 API 过滤、种子管理员、存量歌单迁移。
- Phase 2：前台自助资料（昵称、用户名、头像、改密）与 `GET /auth/me` presigned 头像。
- Phase 3：后台用户管理 CRUD（软删、启禁、角色、初始密码）。

**Non-Goals:**

- 自助注册、OAuth/第三方登录、邮箱验证、多因素认证。
- 曲库按用户隔离、每用户私有歌曲数据。
- 管理员在后台壳改个人资料（统一走前台用户菜单）。
- 管理员查看/编辑他人歌单。
- Redis 会话存储（首版 SQLite 会话表即可）。

## Decisions

### 1. 分阶段交付

| Phase | 范围 | 可独立验收 |
|-------|------|------------|
| **1** | User/Session 模型、登录页、Cookie 会话、全 API 鉴权、admin 门禁、playlist `user_id` + 迁移 | 登录后能用自己的歌单；未登录 401；admin 可进后台 |
| **2** | `/users/me` 资料/密码/头像、前台菜单接线、`/auth/me` presigned | 侧栏显示真实用户；可改昵称/用户名/头像/密码 |
| **3** | 后台「用户管理」页与 `/admin/users*` API | 管理员可开户、改角色、禁用、软删 |

**理由**：Phase 1 解决安全基线与歌单归属；Phase 2/3 可并行准备 UI 但按序合并降低回归面。

### 2. 会话：HttpOnly Cookie + `sessions` 表

- 登录成功：创建 `sessions` 行（`id` 随机 token 或 UUID、`user_id`、`expires_at`），`Set-Cookie: session_id=...; HttpOnly; SameSite=Lax; Path=/`。
- 请求：`get_current_user` 从 Cookie 查 session → user；校验 `user.is_active` 且 `user.deleted_at IS NULL`。
- 登出：删除当前 session 行并清 Cookie。
- **禁用用户**：`UPDATE sessions DELETE WHERE user_id = ?`（同事务或紧随 `is_active=false`）。
- **备选 JWT**：未选——静态同源壳下服务端 session 更易登出/踢人。

### 3. 密码复杂度

须同时满足（创建用户、改密、种子管理员首次设置均适用）：

- 长度 ≥ 8
- 至少 1 个大写字母、1 个小写字母、1 个数字
- 至少 1 个特殊字符（非字母数字，如 `!@#$%^&*`）

校验在服务端统一函数；失败返回 400 与明确中文说明。哈希：**bcrypt**（`passlib`）或 **argon2**（二选一，实现时固定一种）。

### 4. 用户模型与软删除

```text
users
  id, username (unique, 登录标识，可改)
  password_hash
  nickname (展示名，可空则回退 username)
  avatar_object_key (nullable, 如 avatar/42.jpg)
  role: enum admin | user
  is_active: bool default true
  deleted_at: datetime nullable  -- 软删
  created_at, updated_at
```

- **软删**：`deleted_at` 非空视为不存在；登录拒绝；列表默认不展示；用户名**不**立即复用（保留 unique，或实现「删后 username 加后缀」——采用 **保留 username 唯一、软删用户不可登录**）。
- **改 username**：登录用户（含 admin 自己）可通过自助 API 修改；校验格式（如 `^[a-zA-Z0-9_]{3,32}$`）及唯一性（排除自身与未删用户）。

### 5. 种子管理员与存量歌单

- 环境变量：`ADMIN_USERNAME`、`ADMIN_PASSWORD`（仅当 `users` 表无用户时创建一次）。
- `ensure_schema`：加列 `playlists.user_id`；将现有行 `UPDATE playlists SET user_id = <seed_admin_id>`；删全局 `UNIQUE(name)`，加 `UNIQUE(user_id, name)` 或应用层忽略大小写冲突（与现行为一致但在 user 维度）。
- `sort_order`：`max(sort_order) WHERE user_id = current` 计算新歌单权重。

### 6. 头像存储与展示

- Key：`avatar/{user_id}.{ext}`（扩展名来自上传，限制 jpg/jpeg/png/webp；单文件上限如 2MB）。
- 桶：`settings.s3_bucket_music`（与音频同桶）。
- 上传：`POST /users/me/avatar` multipart → `upload_file` → 更新 `avatar_object_key` → 删除旧 key（若有）。
- 展示：`GET /auth/me` 响应含 `avatar_url`（`create_presigned_get_url(avatar_object_key)`，TTL 使用现有 `s3_presign_expire_seconds` 或略短）；前端侧栏 `<img>` 或 background；无头像时首字母占位。

### 7. API 鉴权分层

```text
公开：GET /login (HTML), POST /auth/login, GET /health
需登录：其余业务 API（含 /playlists*, /songs*, 流式播放等）
需 admin：/admin/* 页面路由守卫 + 前缀 /admin/ 下治理 API（含 /admin/users*）
```

- FastAPI：`dependencies=[Depends(require_user)]` 挂 `APIRouter` 或 `app` 默认依赖；公开路由显式 `dependencies=[]`。
- 静态页：`GET /` 与 `GET /admin` 可在服务端读 Cookie 重定向，或 HTML 加载后 `fetch /auth/me` 跳转（优先 **API 401 + 前端统一跳转** 以减少服务端分叉）。

### 8. 前台 / 后台壳分工

- 前台菜单：个人资料、改密码、进入后台（`role===admin` 时显示）、退出登录。
- 后台菜单：仅返回前台 + 退出；**不** duplicated 资料入口。
- `request()`：遇 401 → `location.href = '/login?next=' + encodeURIComponent(path)`。

### 9. 用户管理 API（Phase 3）

- `GET /admin/users` 列表（不含软删，或 `?include_deleted=` 仅 admin 调试）
- `POST /admin/users` 创建（username、初始密码、nickname、role）
- `PATCH /admin/users/{id}` 改 role、is_active、nickname（**不**在此改他人 username，避免支持纠纷；他人 username 若需改可 PATCH 扩展或仅自助）
- `DELETE /admin/users/{id}` → 设 `deleted_at`、踢会话；**禁止**删除最后一个 active admin

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| **BREAKING** 现有集成无 Cookie | README + `.env.example` 文档；可选 dev-only 旁路（**不实现**，避免泄露） |
| presigned URL 过期侧栏头像裂图 | 页面 focus/定时 refresh `/auth/me`；或 401 时整页重登 |
| 改 username 后会话仍有效 | 允许；username 仅标识，session 绑 `user_id` |
| 软删后用户名占用 | 产品接受；必要时管理员物理清理库 |
| SQLite session 表并发 | 单用户 MVP 足够；日后可换 Redis |
| 全 API 鉴权遗漏端点 | Phase 1 checklist + 冒烟：未带 Cookie 访问 `/songs` 须 401 |

## Migration Plan

1. 部署前备份 `music.db`（或生产库）。
2. 发布含 `ensure_schema` 的版本：建 `users`/`sessions`、种子 admin、`playlists.user_id` 回填。
3. 配置 `ADMIN_USERNAME`/`ADMIN_PASSWORD` 于**首次**空库启动；已有库则依赖迁移脚本将歌单挂到已存在 admin（若尚无 admin 则创建）。
4. 通知用户：所有客户端须登录；旧书签 `/admin` 未登录会跳转 `/login`。
5. **回滚**：恢复 DB 备份 + 回退二进制；无向下兼容会话。

## Open Questions

- （已关闭）头像展示：presigned in `/auth/me` ✓
- （已关闭）歌单迁移：方案 1 ✓
- Phase 3 是否允许管理员**重置他人密码**（建议：`POST /admin/users/{id}/reset-password` 生成临时密码或设新密码）——tasks 中纳入，spec 写明。
