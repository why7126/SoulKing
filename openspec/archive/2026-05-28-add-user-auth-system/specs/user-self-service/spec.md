## ADDED Requirements

### Requirement: 修改个人资料

已登录用户 SHALL 可通过 `PATCH /users/me` 更新昵称（`nickname`）与用户名（`username`）。用户名修改须满足格式与唯一性约束（在未软删用户中唯一，排除自身）。昵称可为空，展示时回退为用户名。

#### Scenario: 修改昵称成功

- **GIVEN** 用户已登录
- **WHEN** 客户端提交合法昵称
- **THEN** 响应包含更新后的昵称
- **AND** 后续 `/auth/me` 反映新昵称

#### Scenario: 修改用户名成功

- **GIVEN** 用户已登录且新用户名未被占用
- **WHEN** 客户端提交合法新用户名
- **THEN** 用户名更新成功
- **AND** 用户仍可使用新用户名登录

#### Scenario: 用户名冲突

- **GIVEN** 另一未软删用户已占用该用户名
- **WHEN** 当前用户尝试改为相同用户名
- **THEN** 返回 400 表示用户名已存在

#### Scenario: 管理员修改自己的用户名

- **GIVEN** 当前用户角色为 `admin`
- **WHEN** 管理员通过 `/users/me` 修改自己的用户名
- **THEN** 与普通用户相同规则适用且允许成功

### Requirement: 修改密码

已登录用户 SHALL 可通过 `POST /users/me/password` 提交当前密码与新密码；须校验当前密码正确且新密码满足 `application-auth` 中的复杂度要求。

#### Scenario: 当前密码错误

- **GIVEN** 用户已登录
- **WHEN** 提交的当前密码不正确
- **THEN** 返回 400 或 401（实现统一即可，文档约定一种）

#### Scenario: 修改成功

- **GIVEN** 当前密码正确且新密码满足复杂度
- **WHEN** 客户端提交改密请求
- **THEN** 密码哈希更新
- **AND** 可使用新密码登录

### Requirement: 上传头像

已登录用户 SHALL 可通过 `POST /users/me/avatar` 上传图片（允许 `image/jpeg`、`image/png`、`image/webp`；单文件大小上限由实现约定并在错误时返回 400）。服务端将对象写入 `music-files` 桶，键名为 `avatar/{user_id}.{ext}`，更新用户的 `avatar_object_key`，并删除该用户先前的头像对象（若存在）。

#### Scenario: 上传成功

- **GIVEN** 用户已登录且文件类型与大小合法
- **WHEN** 客户端上传头像
- **THEN** 对象存储于 `avatar/` 前缀下
- **AND** `/auth/me` 返回新的 `avatar_url`

#### Scenario: 类型非法

- **GIVEN** 上传文件非允许的图片类型
- **WHEN** 客户端提交上传
- **THEN** 返回 400

### Requirement: 前台用户菜单接入自助能力

前台壳用户菜单中的「个人资料」「修改密码」SHALL 打开壳内表单或模态（非永久 toast 占位），调用上述 API。管理员与普通用户使用相同入口修改自己的资料与密码。

#### Scenario: 个人资料非占位

- **GIVEN** 用户已登录并打开前台壳
- **WHEN** 用户激活「个人资料」并完成保存
- **THEN** 调用 `PATCH /users/me` 且侧栏展示更新后的昵称或用户名

#### Scenario: 修改密码非占位

- **GIVEN** 用户已登录
- **WHEN** 用户通过菜单修改密码且输入满足复杂度
- **THEN** 调用 `POST /users/me/password` 且提示成功
