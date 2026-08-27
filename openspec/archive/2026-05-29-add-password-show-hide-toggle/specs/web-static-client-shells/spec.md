## MODIFIED Requirements

### Requirement: 登录页

系统 SHALL 提供独立登录页（`GET /login`），包含用户名、密码输入与提交控件；视觉风格与前台 SoulKing Studio 深色主题一致。不提供服务端自助注册入口。登录成功后 SHALL 跳转至 `next` 查询参数指定的路径（若合法且同源），否则跳转站点根路径 `/`。

密码输入框 MUST 在字段右侧提供可聚焦的「显示/隐藏密码」切换按钮；默认掩码显示（`type="password"`）。用户激活切换按钮时，该字段 SHALL 在明文（`type="text"`）与掩码之间切换，并更新按钮的 `aria-label` 与 `aria-pressed` 以反映当前状态。

#### Scenario: 未登录访问前台被引导登录

- **GIVEN** 用户无有效会话并打开前台壳
- **WHEN** 壳内初始化请求 `/auth/me` 返回 401
- **THEN** 浏览器导航至 `/login`（可携带 `next` 回跳参数）

#### Scenario: 登录成功进入前台

- **GIVEN** 用户在登录页输入正确凭据
- **WHEN** 提交登录表单且服务端返回成功
- **THEN** 浏览器进入前台壳根路径或 `next` 目标

#### Scenario: 登录页切换密码可见性

- **GIVEN** 用户在登录页且密码字段已有输入
- **WHEN** 用户激活密码字段旁的显示/隐藏切换按钮
- **THEN** 密码字段在掩码与明文显示之间切换
- **AND** 切换按钮的 `aria-pressed` 与当前可见状态一致
