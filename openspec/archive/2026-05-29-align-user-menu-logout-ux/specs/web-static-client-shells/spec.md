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

用户激活「退出登录」时，系统 MUST 先关闭用户菜单，再通过 **Studio 皮肤专用确认弹层**（`#logoutConfirmOverlay`，结构对齐 `sk-self-service-overlay` / `sk-modal-card`，MUST NOT 使用 Hermes 全局 `#modalOverlay` / `openModal`）询问是否退出；用户确认后 SHALL 调用 `POST /auth/logout` 并导航至 `/login`；取消时不执行登出。

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

#### Scenario: 退出登录呈现危险样式与分隔

- **GIVEN** 用户已展开前台侧栏用户菜单
- **WHEN** 用户查看「退出登录」菜单项
- **THEN** 该项使用危险色强调且与上一菜单项之间存在可见分隔
- **AND** 该项样式与后台壳用户菜单中的「退出登录」危险样式一致

#### Scenario: 退出登录需 Studio 确认弹层

- **GIVEN** 用户已展开前台侧栏用户菜单
- **WHEN** 用户激活「退出登录」
- **THEN** 用户菜单关闭
- **AND** 出现 Studio 皮肤的退出确认弹层（非 Hermes `#modalOverlay`）
- **AND** 弹层使用 `--sk-panel` / `--sk-border` 层级与 Studio 主/次按钮样式

#### Scenario: 取消退出不执行登出

- **GIVEN** 用户已通过「退出登录」打开 Studio 退出确认弹层
- **WHEN** 用户选择取消、关闭按钮或点击遮罩关闭
- **THEN** 不调用登出 API
- **AND** 用户仍停留在当前前台页面

#### Scenario: 确认退出跳转登录页

- **GIVEN** 用户已通过「退出登录」打开 Studio 退出确认弹层
- **WHEN** 用户在弹层中确认退出
- **THEN** 调用 `POST /auth/logout`
- **AND** 浏览器导航至 `/login`

### Requirement: 后台壳侧栏底部用户菜单

后台壳侧栏底部 SHALL 提供用户头像按钮与用户元信息行（数据来自 `/auth/me`）；用户点击头像按钮时 SHALL 展开向上弹出的菜单，包含 **返回前台** 与 **退出登录** 两项。菜单打开/关闭语义 MUST 使用 `role="menu"` / `role="menuitem"` 与 `aria-expanded`。

「返回前台」SHALL 触发整页导航至站点根路径。

「退出登录」菜单项 MUST 携带显式危险样式 class（`user-menu-item--destructive`），视觉与前台一致（危险色 + 顶部分隔 + hover 淡红背景），且 MUST NOT 仅依赖 `:last-child` 等着色。

「退出登录」与「返回前台」之间 MUST 呈现可见分隔。

用户激活「退出登录」时，系统 MUST 先关闭用户菜单，再通过 **Admin 皮肤专用确认弹层**（`#logoutConfirmOverlay`，MUST NOT 使用 Hermes `#modalOverlay` / `openModal`）确认；确认后 SHALL 调用 `POST /auth/logout` 并导航至 `/login`；取消时不执行登出。后台壳 **不** 提供个人资料/改密码菜单项（管理员在前台用户菜单完成）。

#### Scenario: 点击头像展开后台用户菜单

- **GIVEN** 管理员已登录并打开后台壳
- **WHEN** 用户点击侧栏底部用户头像按钮
- **THEN** 弹出包含返回前台、退出登录的菜单

#### Scenario: 后台退出登录危险样式与分隔

- **GIVEN** 用户已展开后台侧栏用户菜单
- **WHEN** 用户查看菜单项
- **THEN** 「退出登录」为危险色强调
- **AND** 「返回前台」与「退出登录」之间存在可见分隔

#### Scenario: 后台退出登录需 Admin 确认弹层

- **GIVEN** 用户已展开后台侧栏用户菜单
- **WHEN** 用户激活「退出登录」
- **THEN** 用户菜单关闭
- **AND** 出现 Admin 皮肤的退出确认弹层（非 Hermes `#modalOverlay`）

#### Scenario: 后台取消退出

- **GIVEN** 用户已打开 Admin 退出确认弹层
- **WHEN** 用户取消或关闭弹层
- **THEN** 不调用登出 API
- **AND** 用户仍停留在当前后台页面

#### Scenario: 后台确认退出跳转登录页

- **GIVEN** 用户已打开 Admin 退出确认弹层
- **WHEN** 用户确认退出
- **THEN** 调用 `POST /auth/logout`
- **AND** 浏览器导航至 `/login`
