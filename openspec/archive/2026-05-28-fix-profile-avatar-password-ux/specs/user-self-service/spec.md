## MODIFIED Requirements

### Requirement: 修改个人资料

已登录用户 SHALL 可通过 `PATCH /users/me` 更新昵称（`nickname`）。**前台壳**个人资料入口 MUST NOT 提供用户名编辑；用户名作为唯一登录标识仅展示，变更须通过后台用户管理（或其它非前台自助入口）完成。昵称可为空，展示时回退为用户名。

后台或其它客户端若调用 `PATCH /users/me` 并提交 `username`，仍适用格式与唯一性约束（在未软删用户中唯一，排除自身）。

#### Scenario: 修改昵称成功

- **GIVEN** 用户已登录
- **WHEN** 客户端提交合法昵称
- **THEN** 响应包含更新后的昵称
- **AND** 后续 `/auth/me` 反映新昵称

#### Scenario: 前台不提交用户名变更

- **GIVEN** 用户已登录并在前台打开个人资料
- **WHEN** 用户保存资料
- **THEN** 请求体不包含 `username` 字段（或等价：前台脚本不发送用户名）
- **AND** 服务端用户名保持不变

#### Scenario: 修改用户名成功（非前台自助）

- **GIVEN** 用户已登录且新用户名未被占用
- **WHEN** 具备权限的客户端（如后台管理）提交合法新用户名
- **THEN** 用户名更新成功
- **AND** 用户仍可使用新用户名登录

#### Scenario: 用户名冲突

- **GIVEN** 另一未软删用户已占用该用户名
- **WHEN** 客户端尝试改为相同用户名
- **THEN** 返回 400 表示用户名已存在

#### Scenario: 管理员修改自己的用户名

- **GIVEN** 当前用户角色为 `admin`
- **WHEN** 管理员通过后台等非前台自助入口修改自己的用户名
- **THEN** 与普通用户相同规则适用且允许成功

### Requirement: 修改密码

已登录用户 SHALL 可通过 `POST /users/me/password` 提交当前密码与新密码；须校验当前密码正确且新密码满足 `application-auth` 中的复杂度要求。

**前台壳**修改密码表单 MUST 提供「确认新密码」字段；仅当当前密码已填、两次新密码一致且新密码满足复杂度时，「保存」按钮才可点击（非 disabled）；提交前客户端 SHALL 执行相同规则校验。

#### Scenario: 当前密码错误

- **GIVEN** 用户已登录
- **WHEN** 提交的当前密码不正确
- **THEN** 返回 400 或 401（实现统一即可，文档约定一种）

#### Scenario: 修改成功

- **GIVEN** 当前密码正确且新密码满足复杂度
- **WHEN** 客户端提交改密请求
- **THEN** 密码哈希更新
- **AND** 可使用新密码登录

#### Scenario: 前台两次新密码不一致

- **GIVEN** 用户在前台修改密码弹层
- **WHEN** 新密码与确认新密码不一致
- **THEN** 「保存」按钮保持禁用
- **AND** 不发起 `POST /users/me/password`

#### Scenario: 前台新密码不满足复杂度

- **GIVEN** 用户在前台修改密码弹层
- **WHEN** 新密码未满足复杂度且确认字段与其一致
- **THEN** 「保存」按钮保持禁用

### Requirement: 上传头像

已登录用户 SHALL 可通过 `POST /users/me/avatar` 上传图片（允许 `image/jpeg`、`image/png`、`image/webp`；单文件大小上限由实现约定并在错误时返回 400）。服务端将对象写入 `music-files` 桶，键名为 `avatar/{user_id}.{ext}`，更新用户的 `avatar_object_key`，并删除该用户先前的头像对象（若存在）。

上传成功或刷新 `/auth/me` 后，**前台壳**侧栏头像与个人资料弹层预览 MUST 展示最新头像（含对同一对象使用 cache-bust 参数以避免浏览器缓存旧图）。

#### Scenario: 上传成功

- **GIVEN** 用户已登录且文件类型与大小合法
- **WHEN** 客户端上传头像
- **THEN** 对象存储于 `avatar/` 前缀下
- **AND** `/auth/me` 返回新的 `avatar_url`
- **AND** 前台侧栏与个人资料预览可见新头像

#### Scenario: 类型非法

- **GIVEN** 上传文件非允许的图片类型
- **WHEN** 客户端提交上传
- **THEN** 返回 400

### Requirement: 前台用户菜单接入自助能力

前台壳用户菜单中的「个人资料」「修改密码」SHALL 打开壳内表单或模态（非永久 toast 占位），调用上述 API。管理员与普通用户使用相同入口修改自己的资料与密码。

个人资料模态 SHALL 展示当前用户头像预览：若 `/auth/me` 提供 `avatar_url` 则显示该图片；否则显示与侧栏一致的用户名首字母（或等价）占位。模态 MUST 以只读方式展示用户名，不提供用户名编辑控件。模态与改密模态的视觉 MUST 符合 `web-static-client-shells` 中「前台壳个人资料与修改密码弹层 Studio 视觉」要求。

#### Scenario: 个人资料非占位

- **GIVEN** 用户已登录并打开前台壳
- **WHEN** 用户激活「个人资料」并完成保存（昵称或头像）
- **THEN** 调用 `PATCH /users/me` 和/或 `POST /users/me/avatar`
- **AND** 侧栏展示更新后的昵称或用户名回退展示

#### Scenario: 个人资料用户名只读

- **GIVEN** 用户已登录并打开「个人资料」模态
- **WHEN** 用户查看用户名区域
- **THEN** 用户名为只读展示且不可编辑

#### Scenario: 修改密码非占位

- **GIVEN** 用户已登录
- **WHEN** 用户通过菜单修改密码且输入满足复杂度且两次新密码一致
- **THEN** 调用 `POST /users/me/password` 且提示成功

#### Scenario: 个人资料展示头像预览

- **GIVEN** 用户已登录且 `/auth/me` 返回 `avatar_url`
- **WHEN** 用户打开「个人资料」模态
- **THEN** 模态内可见当前头像图片预览

#### Scenario: 上传头像后预览与侧栏同步

- **GIVEN** 用户在个人资料模态中上传新头像并保存成功
- **WHEN** 保存完成
- **THEN** 模态内预览与侧栏头像均显示新图片

#### Scenario: 无头像时展示占位

- **GIVEN** 用户已登录且 `/auth/me` 无 `avatar_url`
- **WHEN** 用户打开「个人资料」模态
- **THEN** 模态内展示与侧栏一致的首字母（或等价）头像占位
