## MODIFIED Requirements

### Requirement: 前台用户菜单接入自助能力

前台壳用户菜单中的「个人资料」「修改密码」SHALL 打开壳内表单或模态（非永久 toast 占位），调用上述 API。管理员与普通用户使用相同入口修改自己的资料与密码。

个人资料模态 SHALL 展示当前用户头像预览：若 `/auth/me` 提供 `avatar_url` 则显示该图片；否则显示与侧栏一致的用户名首字母（或等价）占位。模态与改密模态的视觉 MUST 符合 `web-static-client-shells` 中「前台壳个人资料与修改密码弹层 Studio 视觉」要求。

#### Scenario: 个人资料非占位

- **GIVEN** 用户已登录并打开前台壳
- **WHEN** 用户激活「个人资料」并完成保存
- **THEN** 调用 `PATCH /users/me` 且侧栏展示更新后的昵称或用户名

#### Scenario: 修改密码非占位

- **GIVEN** 用户已登录
- **WHEN** 用户通过菜单修改密码且输入满足复杂度
- **THEN** 调用 `POST /users/me/password` 且提示成功

#### Scenario: 个人资料展示头像预览

- **GIVEN** 用户已登录且 `/auth/me` 返回 `avatar_url`
- **WHEN** 用户打开「个人资料」模态
- **THEN** 模态内可见当前头像图片预览

#### Scenario: 无头像时展示占位

- **GIVEN** 用户已登录且 `/auth/me` 无 `avatar_url`
- **WHEN** 用户打开「个人资料」模态
- **THEN** 模态内展示与侧栏一致的首字母（或等价）头像占位
