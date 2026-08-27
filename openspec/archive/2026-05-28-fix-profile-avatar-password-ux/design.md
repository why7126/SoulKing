## Context

- 认证与自助 API 已上线：`POST /users/me/avatar` 返回 `AuthMeOut`（含 `avatar_url`），`GET /auth/me` 通过 S3 presigned GET 提供头像 URL；对象键为 `avatar/{user_id}.{ext}`，同扩展名覆盖上传时 URL 路径不变，浏览器易缓存旧图。
- 前台 `frontend.js` 在 `saveProfile()` 中上传头像后调用 `loadAuthMe()` 与 `renderFrontUserSidebar()`，但未对 URL 做 cache-bust；`renderProfileAvatarPreview()` 未设置与侧栏一致的 `backgroundSize` / `backgroundPosition`（部分依赖 CSS，侧栏为内联设置）。
- 个人资料弹层仍含可编辑 `#profileUsernameInput`，保存时随 `PATCH /users/me` 提交 `username`，与产品「前台不可改登录名」不一致。
- 改密弹层仅有「当前密码」「新密码」，保存按钮始终可点，无「确认新密码」与客户端复杂度门禁。

## Goals / Non-Goals

**Goals:**

- 用户更换头像后，侧栏头像与个人资料预览在当次会话内立即可见新图。
- 前台个人资料仅可改昵称与头像；用户名以只读方式展示。
- 改密须两次一致的新密码且满足复杂度后，方可点击保存；减少误提交。

**Non-Goals:**

- 不修改后端密码复杂度规则或 `PATCH /users/me` 的 API 契约（仍可接受 `username`，但前台不传）。
- 不包含后台管理员用户表的 UX（管理员改他人或自己用户名仍走 admin API）。
- 不重做 Studio 皮肤整体（已由 `align-profile-password-ui-with-studio-design` 覆盖）。

## Decisions

### 1. 头像 cache-bust（客户端）

**选择**：在前端封装 `avatarDisplayUrl(url, version)`，在用于 `backgroundImage` 或 `<img src>` 时追加查询参数 `v`，版本取 `user.updated_at`（ISO 字符串或 epoch）或上传成功响应中的时间戳；若无 `updated_at` 则在上传成功后使用 `Date.now()`。

**理由**：对象键稳定、presigned 查询串变化时，路径仍可能被判为同一资源；查询参数 `v` 强制浏览器重新拉取。

**备选**：服务端在 presigned URL 上附加随机 nonce — 增加后端改动，且 `/auth/me` 每次不同 URL 不利于调试；客户端 bust 足够。

### 2. 上传后立即刷新 UI

**选择**：`POST /users/me/avatar` 成功后，用响应体更新 `state.currentUser`，并调用统一的 `renderFrontUserSidebar()` 与 `renderProfileAvatarPreview()`；若用户仍在个人资料弹层内，保持弹层打开并更新预览。

**理由**：避免仅依赖二次 `GET /auth/me` 且未 bust 导致「保存成功但图不变」。

### 3. 用户名前台只读

**选择**：HTML 将用户名改为 `<span>` 或 `readonly` + `disabled` 样式字段（推荐只读文本 + `sk-form-field--readonly`），`saveProfile()` 的 JSON body 仅 `{ nickname }`。

**理由**：登录标识变更应限制在后台管理；减少与普通用户自助混淆。后端 `PATCH` 仍保留 `username` 字段供未来或其它客户端使用。

### 4. 改密确认与保存按钮门禁

**选择**：

- 新增 `#passwordNewConfirmInput`。
- 抽取与 `app/auth.py` 中 `validate_password_complexity` 一致的客户端函数（长度 ≥8、大小写、数字、特殊字符）。
- `#passwordSaveBtn` 默认 `disabled`；在 `input` 事件上计算：`current` 非空 && `new === confirm` && `complexityOk(new)`。
- 提交时仍调用 `POST /users/me/password`，服务端校验不变。

**理由**：符合用户明确要求；降低误操作；与后端规则对齐减少 400 往返。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| presigned URL 已含 `?`，再追加 `&v=` 需正确拼接 | 使用 `URL` API 或统一 helper 解析查询串 |
| `createObjectURL` 预览未 revoke 导致内存泄漏 | 在关闭弹层或新选文件时 `URL.revokeObjectURL` |
| 只读用户名与无障碍（屏幕阅读器） | 使用 `aria-readonly` 或静态文本 + 可见标签 |

## Migration Plan

- 纯前端与 spec 增量，无数据库迁移。
- 部署后用户硬刷新一次即可；已有用户无需数据修复。

## Open Questions

（无 — 范围已由产品输入明确。）
