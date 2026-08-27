## Why

前台在展示用户头像时对 `/auth/me` 返回的 presigned URL 追加未参与签名的 `v` 查询参数做 cache-bust，导致 MinIO/S3 SigV4 验签失败（HTTP 403），侧栏与个人资料预览均无法加载图片。用户上传头像虽已成功写入对象存储，但界面表现为「换了头像却不显示」。此前 `fix-profile-avatar-password-ux` 的客户端 bust 策略与 presigned URL 机制不兼容，需纠正规格与实现。

## What Changes

- **移除错误的客户端 cache-bust**：前台渲染 `#frontUserMenuBtn` 与 `#profileAvatarPreview` 时 MUST 原样使用 API 返回的 `avatar_url`，不得在未重新签发的情况下追加或修改查询参数。
- **保留上传后 UI 刷新**：`POST /users/me/avatar` 成功后仍用响应体更新 `currentUser` 并刷新侧栏与预览；`loadAuthMe()` 后同样刷新。
- **服务端 cache 策略（可选增强）**：上传头像时为对象设置合理的 `Cache-Control`，或在签发 presigned URL 时将 cache-bust 参数纳入签名（见 design.md）；本变更至少保证展示可用。
- **规格修订**：更正 `web-static-client-shells` 与 `user-self-service` 中「客户端追加 `v`」的要求；必要时在 `application-auth` 中明确 presigned URL 不可被客户端篡改。
- **文档**：更新 `ui-design.md` 中头像 cache-bust 描述，与实现一致。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：修正前台头像展示与 cache 相关需求，禁止破坏 presigned 签名。
- `user-self-service`：修正头像上传后展示验收，与 presigned URL 约束一致。
- `application-auth`：补充 `avatar_url` 为已签名 URL、客户端须原样使用的说明（若需）。

## Impact

- `app/static/frontend.js` — 移除或停用 `avatarDisplayUrl` 对 presigned URL 的查询参数追加；保留 blob 本地预览逻辑
- `app/auth_routes.py` / `app/storage.py` — 可选：上传时 `Cache-Control` 或签发时纳入签名参数
- `openspec/specs/web-static-client-shells/spec.md`、`user-self-service/spec.md`、`application-auth/spec.md` — 合并 delta
- `ui-design.md` — 头像展示约定
