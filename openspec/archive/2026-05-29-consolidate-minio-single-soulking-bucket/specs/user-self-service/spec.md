## MODIFIED Requirements

### Requirement: 上传头像

已登录用户 SHALL 可通过 `POST /users/me/avatar` 上传图片（允许 `image/jpeg`、`image/png`、`image/webp`；单文件大小上限由实现约定并在错误时返回 400）。服务端将对象写入 `soulking` 桶，键名为 `avatar/{user_id}.{ext}`，更新用户的 `avatar_object_key`，并删除该用户先前的头像对象（若存在）。

上传成功或刷新 `/auth/me` 后，**前台壳**侧栏头像与个人资料弹层预览 MUST 展示最新头像。展示时 MUST 原样使用 API 返回的 presigned `avatar_url`，不得在客户端追加未参与签名的查询参数。

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
