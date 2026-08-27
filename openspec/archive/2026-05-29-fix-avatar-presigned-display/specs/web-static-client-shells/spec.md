## MODIFIED Requirements

### Requirement: 前台头像展示刷新与 cache-bust

前台脚本在渲染侧栏用户头像（`#frontUserMenuBtn`）与个人资料头像预览（`#profileAvatarPreview`）时，若使用 `/auth/me` 或头像上传响应中的 `avatar_url`，MUST **原样**使用该 URL（不得在客户端追加或修改查询参数，以免破坏 S3/MinIO presigned SigV4 签名）。头像上传成功或 `loadAuthMe()` 后 MUST 立即刷新上述两处展示。本地文件选择预览 MAY 使用 `blob:` 等临时 URL，且不得对 presigned URL 做未签名改写。

#### Scenario: 上传头像后侧栏更新

- **GIVEN** 用户在前台个人资料中上传并保存头像成功
- **WHEN** 保存完成
- **THEN** 侧栏 `#frontUserMenuBtn` 显示新头像图片
- **AND** 浏览器对 `avatar_url` 的请求返回成功（如 200）

#### Scenario: 上传头像后弹层预览更新

- **GIVEN** 用户在前台个人资料中上传并保存头像成功
- **WHEN** 保存完成且弹层仍打开或再次打开
- **THEN** `#profileAvatarPreview` 显示新头像图片

#### Scenario: presigned URL 不被客户端篡改

- **GIVEN** `/auth/me` 返回的 `avatar_url` 为 presigned GET URL
- **WHEN** 前台将其用于侧栏或资料预览
- **THEN** 请求 URL 与 API 返回值一致（除浏览器自身行为外无额外 query 参数）
- **AND** 不得因追加未签名参数导致对象存储返回 403
