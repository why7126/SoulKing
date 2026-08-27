## Why

登录页与修改密码表单中的密码输入框默认为掩码显示，用户在核对复杂密码时容易输错且无法即时发现。为常见表单交互惯例，应在上述密码字段旁提供可切换的「显示/隐藏密码」控件，降低输入错误率并改善可用性。

## What Changes

- 登录页（`login.html`）密码字段增加显示/隐藏切换按钮，点击后在 `password` 与 `text` 输入类型间切换。
- 前台壳修改密码弹层（`#passwordOverlay`）内三个密码字段（当前密码、新密码、确认新密码）各增加独立的显示/隐藏切换。
- 新增可复用的密码输入框 UI 样式与交互逻辑（HTML 结构、CSS、少量 JS），视觉与现有 SoulKing Studio / 登录页深色主题一致。
- 切换按钮须具备可访问性标签（`aria-label` / `aria-pressed`），键盘可聚焦。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：登录页密码字段须支持显示/隐藏切换。
- `user-self-service`：前台修改密码表单各密码字段须支持显示/隐藏切换。

## Impact

- **前端静态资源**：`app/static/login.html`、`app/static/login.css`、`app/static/login.js`；`app/static/index.html`（密码弹层 markup）；`app/static/studio.css`（密码输入框组件样式）；`app/static/frontend.js`（切换交互初始化）。
- **后端 API**：无变更。
- **依赖**：无新依赖。
