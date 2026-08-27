## ADDED Requirements

### Requirement: 登录页

系统 SHALL 提供独立登录页（`GET /login`），包含用户名、密码输入与提交控件；视觉风格与前台 SoulKing Studio 深色主题一致。不提供服务端自助注册入口。登录成功后 SHALL 跳转至 `next` 查询参数指定的路径（若合法且同源），否则跳转站点根路径 `/`。

#### Scenario: 未登录访问前台被引导登录

- **GIVEN** 用户无有效会话并打开前台壳
- **WHEN** 壳内初始化请求 `/auth/me` 返回 401
- **THEN** 浏览器导航至 `/login`（可携带 `next` 回跳参数）

#### Scenario: 登录成功进入前台

- **GIVEN** 用户在登录页输入正确凭据
- **WHEN** 提交登录表单且服务端返回成功
- **THEN** 浏览器进入前台壳根路径或 `next` 目标

### Requirement: API 请求携带会话与 401 处理

前台与后台壳内 `request()`（或等价封装）SHALL 对 API 请求携带 Cookie（`credentials: 'include'`）。收到 401 时 SHALL 跳转至 `/login`，并附带当前路径为 `next`（若实现安全）。

#### Scenario: 会话过期后操作跳转登录

- **GIVEN** 用户曾登录但会话已失效
- **WHEN** 壳内 API 返回 401
- **THEN** 跳转登录页

### Requirement: 侧栏展示真实用户

前台与后台壳侧栏用户区 SHALL 在加载后请求 `/auth/me` 并展示当前用户昵称（无昵称时用用户名）及头像（使用响应中的 `avatar_url`；无头像时显示用户名首字母等占位）。不得长期硬编码固定展示名（如 SoulKing/Admin）。

#### Scenario: 前台展示昵称与头像

- **GIVEN** 用户已登录且 `/auth/me` 返回昵称与 `avatar_url`
- **WHEN** 前台壳完成初始化
- **THEN** 侧栏用户元信息区显示该昵称
- **AND** 头像按钮展示对应图片

### Requirement: 后台用户管理导航

后台壳侧栏导航 SHALL 包含「用户管理」入口；仅管理员可访问（与页面加载时 `/auth/me` 角色一致）。点击进入用户管理主内容区。

#### Scenario: 用户管理导航可见

- **GIVEN** 管理员已登录后台壳
- **WHEN** 用户查看侧栏导航
- **THEN** 存在「用户管理」项

## MODIFIED Requirements

### Requirement: 前台壳侧栏底部用户菜单

前台壳侧栏底部 SHALL 展示曲库统计（如「X 首歌库」）与用户区。用户区 SHALL 包含用户头像按钮与用户名称展示（数据来自 `/auth/me`），结构对齐后台壳侧栏底部用户行（头像按钮 + 元信息，非整行单一 button）。

用户点击侧栏底部的 **头像按钮**（`#frontUserMenuBtn`）时 SHALL 展开向上弹出的菜单，包含：**个人资料**、**修改密码**、**进入后台**（仅当前用户角色为 `admin` 时显示或可用）、**退出登录**。曲库统计行 MUST NOT 作为菜单触发器。

菜单在展开后 MUST 保持可见，直至用户点击菜单与触发按钮之外、或选择某一菜单项后关闭；MUST NOT 因与打开菜单同一次用户激活相关联的 outside-click 或菜单项 handler 时序而立即关闭。

顶栏 SHALL **不** 包含用户头像、用户名或用户菜单等重复入口。

「个人资料」「修改密码」SHALL 调用 `user-self-service` 所定义 API，不得以永久「即将接入」toast 代替。

「进入后台」SHALL 触发整页导航至管理入口路径；仅 `admin` 角色可见或点击；`user` 角色不得看到该菜单项。

「退出登录」菜单项 MUST 携带显式危险样式 class（`user-menu-item--destructive`），文字颜色与各壳 `--sk-danger` / `--adm-danger` 一致，hover 时呈现淡红背景，且 MUST NOT 仅依赖 `:last-child` 实现危险色。

「退出登录」与其上一菜单项之间 MUST 呈现可见分隔。

用户激活「退出登录」时，系统 MUST 先关闭用户菜单，再通过 `#modalOverlay` / `openModal` 确认；用户确认后 SHALL 调用 `POST /auth/logout` 并导航至 `/login`；取消时不执行登出。

#### Scenario: 点击头像展开菜单

- **GIVEN** 用户已登录并打开前台壳且用户菜单未展开
- **WHEN** 用户点击侧栏底部用户区的头像按钮
- **THEN** 在侧栏底部上方弹出菜单
- **AND** 管理员可见「进入后台」，普通用户不可见该项

#### Scenario: 菜单展开后保持可见

- **GIVEN** 用户已登录并打开前台壳且用户菜单未展开
- **WHEN** 用户点击侧栏底部的头像按钮一次
- **THEN** 用户菜单保持展开状态
- **AND** 用户可看到并点击菜单中的任一项

#### Scenario: 进入后台

- **GIVEN** 当前用户角色为 `admin` 且已展开侧栏用户菜单
- **WHEN** 用户激活「进入后台」
- **THEN** 浏览器导航至管理入口路径

#### Scenario: 点击外部关闭菜单

- **GIVEN** 用户已展开侧栏用户菜单
- **WHEN** 用户在菜单与头像触发按钮外点击
- **THEN** 用户菜单关闭

#### Scenario: 顶栏不含用户菜单入口

- **GIVEN** 用户打开前台壳页面
- **WHEN** 用户查看顶栏右侧区域
- **THEN** 不存在用户头像、用户名或用户下拉菜单控件

#### Scenario: 退出登录需确认

- **GIVEN** 用户已展开前台侧栏用户菜单
- **WHEN** 用户激活「退出登录」
- **THEN** 用户菜单关闭
- **AND** 出现确认退出的对话框

#### Scenario: 取消退出不执行登出

- **GIVEN** 用户已通过「退出登录」打开确认对话框
- **WHEN** 用户选择取消或关闭对话框
- **THEN** 不调用登出 API
- **AND** 用户仍停留在当前前台页面

#### Scenario: 确认退出跳转登录页

- **GIVEN** 用户已通过「退出登录」打开确认对话框
- **WHEN** 用户在对话框中确认退出
- **THEN** 调用 `POST /auth/logout`
- **AND** 浏览器导航至 `/login`

### Requirement: 后台壳侧栏底部用户菜单

后台壳侧栏底部 SHALL 提供用户头像按钮与用户元信息行（数据来自 `/auth/me`）；用户点击头像按钮时 SHALL 展开向上弹出的菜单，包含 **返回前台** 与 **退出登录** 两项。菜单打开/关闭语义 MUST 使用 `role="menu"` / `role="menuitem"` 与 `aria-expanded`。

「返回前台」SHALL 触发整页导航至站点根路径。

「退出登录」样式与确认流程同前台；确认后 SHALL 调用 `POST /auth/logout` 并导航至 `/login`。后台壳 **不** 提供个人资料/改密码菜单项（管理员在前台用户菜单完成）。

#### Scenario: 点击头像展开后台用户菜单

- **GIVEN** 管理员已登录并打开后台壳
- **WHEN** 用户点击侧栏底部用户头像按钮
- **THEN** 弹出包含返回前台、退出登录的菜单

#### Scenario: 后台确认退出跳转登录页

- **GIVEN** 用户已打开退出确认对话框
- **WHEN** 用户确认退出
- **THEN** 调用 `POST /auth/logout`
- **AND** 浏览器导航至 `/login`
