## Why

前台「个人资料」「修改密码」虽已接入 Studio 皮肤，但存在三类影响日常使用的缺陷：上传头像后侧栏与弹窗预览不刷新（用户感知为「没换上」）；个人资料仍允许编辑用户名，与「用户名是唯一登录标识、仅管理员在后台维护」的产品决策冲突；改密仅单次输入新密码且无保存前校验，易误输且不符合常见安全交互。需在规格与实现层一次性收敛这些自助 UX 问题。

## What Changes

- **头像展示修复**：上传成功或 `/auth/me` 刷新后，侧栏 `#frontUserMenuBtn` 与个人资料 `#profileAvatarPreview` MUST 立即显示新头像；对同一对象键的 presigned URL 使用客户端 cache-bust（如 `?v=<updated_at 或时间戳>`）避免浏览器缓存旧图。
- **用户名前台只读**：个人资料弹层将用户名改为只读展示（非可编辑输入框）；前台 `PATCH /users/me` 仅提交 `nickname`（及头像上传），不再提交 `username`。
- **改密二次确认**：修改密码弹层增加「确认新密码」字段；「保存」按钮默认禁用，仅当当前密码已填、两次新密码一致且满足 `application-auth` 复杂度时启用；提交前客户端校验，服务端规则不变。
- **规格更新**：修订 `user-self-service` 与 `web-static-client-shells` 中相关验收场景，与 `ui-design.md` 维护约定一致。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `user-self-service`：前台不得自助改用户名；头像上传后展示刷新；改密须二次确认新密码及保存按钮启用条件。
- `web-static-client-shells`：个人资料/改密弹层 DOM 与交互（只读用户名、确认密码字段、保存按钮 disabled 态）。

## Impact

- `app/static/index.html` — 个人资料用户名展示、改密确认字段、保存按钮初始 `disabled`
- `app/static/frontend.js` — 头像 cache-bust、保存逻辑、改密表单校验与按钮状态
- `app/static/studio.css` — 只读用户名展示样式（若需）
- `openspec/specs/user-self-service/spec.md` — 主 spec 合并 delta
- `openspec/specs/web-static-client-shells/spec.md` — 主 spec 合并 delta
- `ui-design.md` — 可选补充自助表单交互约定
