## Context

- 用户头像存于 `music-files` 桶 `avatar/{user_id}.{ext}`；`GET /auth/me` 与 `POST /users/me/avatar` 通过 `S3Storage.create_presigned_get_url` 返回 SigV4 presigned GET URL。
- 前台 `frontend.js` 中 `avatarDisplayUrl()` 在 presigned URL 上追加未签名的 `v` 查询参数；MinIO 验签失败返回 403，`background-image` 静默失败，用户看到渐变圆或空圆而非照片。
- 已验证：原始 presigned URL 返回 200；追加 `&v=123` 后返回 403。
- MinIO 由并列 ProjectMinio 独立部署属预期架构；展示时浏览器直连 presigned URL 中的 host，与上传路径（服务端 boto3）分离，但本 bug 与 MinIO 是否同容器无关。

## Goals / Non-Goals

**Goals:**

- 侧栏 `#frontUserMenuBtn` 与个人资料 `#profileAvatarPreview` 在存在 `avatar_url` 时能稳定加载并显示图片。
- 上传头像或 `loadAuthMe()` 后立即刷新上述 UI。
- 规格与 `ui-design.md` 不再要求破坏 presigned 签名的客户端 cache-bust。

**Non-Goals:**

- 不引入 `S3_PUBLIC_ENDPOINT_URL` 或应用层头像代理（除非后续单独变更）。
- 不修改对象键命名规则 `avatar/{user_id}.{ext}`。
- 不重做个人资料/改密其他 UX（用户名只读、改密确认等保持现状）。

## Decisions

### 1. 前台原样使用 `avatar_url`（不追加查询参数）

**选择**：删除对 presigned URL 的 `avatarDisplayUrl` / `getAvatarBustVersion` 逻辑；`applyAvatarToElement(el, url)` 仅将 API 返回的 URL 用于 `background-image`。本地文件预览仍用 `blob:` URL，且不经过 presigned。

**理由**：SigV4 签名覆盖 canonical query string；客户端追加参数必然 403。

**备选**：继续在客户端加 `v` — 已证伪，不可行。

### 2. 缓存刷新策略

**选择**：

- 每次 `GET /auth/me` / 上传响应均重新签发 presigned URL（已实现），URL 本体含新 `X-Amz-Date` 与签名，多数情况下足以让浏览器视为新资源。
- 上传头像时在 `upload_file` 为对象设置 `Cache-Control: no-cache`（或 `max-age=0, must-revalidate`），降低同键覆盖后 CDN/浏览器强缓存旧字节的概率。

**理由**：不改动 presigned 契约即可修复「完全不显示」；`Cache-Control` 为低成本增强。

**备选**：签发时将 `updated_at` 作为**已签名**的 query 参数传入 `generate_presigned_url` — 可行但需改 `create_presigned_get_url` 与调用方，本变更非必须。

### 3. 上传后 UI 刷新（保持）

**选择**：`POST /users/me/avatar` 成功后用响应体更新 `state.currentUser`，调用 `renderFrontUserSidebar()` 与 `renderProfileAvatarPreview()`；移除 `state.avatarBust` 状态字段。

**理由**：与现逻辑一致，仅去掉错误的 bust。

### 4. 后台壳

**选择**：`admin.js` 已原样使用 `avatar_url`，无需为修复 403 而改动；实现时确认与前台 `applyAvatarToElement` 行为一致即可。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 同扩展名覆盖上传且浏览器强缓存对象字节 | 上传时设置 `Cache-Control`；每次 me 响应新 presigned URL |
| presigned URL 中 host（如 `host.docker.internal`）浏览器不可达 | 属部署配置问题，README 已说明 Docker vs 本机 `S3_ENDPOINT_URL`；不在本变更范围 |
| 移除 `avatarBust` 后无回归测试 | 手工：上传头像 → 侧栏与弹层可见；Network 中头像 GET 为 200 |

## Migration Plan

- 纯前端为主的小修正 + 可选上传元数据；无数据库迁移。
- 部署后用户硬刷新一次即可。

## Open Questions

（无）
