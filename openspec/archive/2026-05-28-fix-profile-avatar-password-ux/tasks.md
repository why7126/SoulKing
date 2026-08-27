## 1. 头像展示与 cache-bust

- [x] 1.1 在 `frontend.js` 新增 `avatarDisplayUrl(url, version)` helper，安全拼接 `v` 查询参数
- [x] 1.2 更新 `renderFrontUserSidebar()` 与 `renderProfileAvatarPreview()`：有 `avatar_url` 时使用 helper，并统一设置 `backgroundSize` / `backgroundPosition`（与侧栏一致）
- [x] 1.3 修改 `saveProfile()`：头像上传成功后用响应体更新 `state.currentUser`，立即刷新侧栏与预览；`loadAuthMe()` 后同样带 bust 版本（优先 `updated_at`）
- [x] 1.4 文件选择预览：`URL.createObjectURL` 在关闭弹层或重选文件时 `revokeObjectURL`

## 2. 个人资料用户名只读

- [x] 2.1 重构 `index.html`：将 `#profileUsernameInput` 改为只读展示（静态文本 + 标签，或 `readonly` 字段 + `sk-form-field--readonly`）
- [x] 2.2 在 `studio.css` 补充只读用户名字段样式（若需要）
- [x] 2.3 修改 `openProfileOverlay()`：填充只读用户名；`saveProfile()` 的 `PATCH` body 仅含 `{ nickname }`

## 3. 修改密码二次确认与保存门禁

- [x] 3.1 在 `index.html` 的 `#passwordOverlay` 增加「确认新密码」字段；`#passwordSaveBtn` 默认 `disabled`
- [x] 3.2 在 `frontend.js` 抽取 `passwordMeetsComplexity(pw)`（与 `auth.validate_password_complexity` 规则一致）
- [x] 3.3 实现 `updatePasswordSaveEnabled()`：监听三个密码框 `input`，控制保存按钮 disabled
- [x] 3.4 在 `openPasswordOverlay()` 重置字段并禁用保存；`savePassword()` 提交前再次校验两次新密码一致

## 4. 验收与文档

- [x] 4.1 手动验证：上传头像后侧栏与弹层预览均更新；重复上传同格式仍可见新图
- [x] 4.2 手动验证：个人资料无法改用户名；昵称保存正常
- [x] 4.3 手动验证：改密保存按钮仅在条件满足时可点；不一致或弱密码时不可提交
- [x] 4.4 更新 `ui-design.md` 侧栏用户菜单 / 自助表单小节（只读用户名、确认密码、头像 bust 约定）
