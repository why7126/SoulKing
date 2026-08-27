## 1. 前台头像展示修复

- [x] 1.1 在 `frontend.js` 移除 `avatarDisplayUrl`、`getAvatarBustVersion`、`state.avatarBust` 及对 presigned URL 的查询参数追加
- [x] 1.2 简化 `applyAvatarToElement`：对 API 返回的 `avatar_url` 原样设置 `background-image`；`blob:` 预览路径保持不变
- [x] 1.3 确认 `saveProfile()` 上传成功后仍更新 `state.currentUser` 并调用 `renderFrontUserSidebar()`、`renderProfileAvatarPreview()`
- [x] 1.4 手工验证：DevTools 中头像 GET 为 200、URL 无额外 `v=`；侧栏与资料弹层均显示图片

## 2. 服务端缓存（可选增强）

- [x] 2.1 头像 `upload_file` 时设置 `Cache-Control: no-cache`（或 `max-age=0, must-revalidate`），避免同键覆盖后浏览器强缓存旧字节

## 3. 文档与规格

- [x] 3.1 更新 `ui-design.md` 头像展示说明：禁止对 presigned URL 客户端追加未签名参数；说明依赖重新签发与可选 `Cache-Control`
- [x] 3.2 归档前将本 change 的 spec delta 合并入主 spec（`/opsx:archive` 流程）
