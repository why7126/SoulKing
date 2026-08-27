## ADDED Requirements

### Requirement: 前台个人资料用户名只读展示

前台壳 `#profileOverlay`（或等价个人资料模态）中的用户名 MUST 以只读文本或等效不可编辑控件展示；MUST NOT 使用可提交的文本输入框供用户修改登录名。保存资料时前台脚本 MUST 仅向 `PATCH /users/me` 发送 `nickname`（及通过独立接口上传头像），不发送 `username`。

#### Scenario: 个人资料弹层用户名不可编辑

- **GIVEN** 用户已登录并打开前台个人资料弹层
- **WHEN** 用户尝试修改用户名字段
- **THEN** 无法编辑用户名（只读或静态文本）
- **AND** 保存请求不包含 `username`

### Requirement: 前台修改密码二次确认与保存门禁

前台壳 `#passwordOverlay`（或等价改密模态）MUST 包含字段：当前密码、新密码、确认新密码。`#passwordSaveBtn`（或等价主按钮）在页面打开时 MUST 为 `disabled`；仅当当前密码非空、新密码与确认新密码一致且新密码满足与 `application-auth` 一致的复杂度规则时，按钮才可启用。

#### Scenario: 改密弹层含确认字段

- **GIVEN** 用户打开前台修改密码弹层
- **WHEN** 解析表单字段
- **THEN** 存在「确认新密码」输入框

#### Scenario: 保存按钮默认禁用

- **GIVEN** 用户刚打开修改密码弹层
- **WHEN** 尚未满足全部校验条件
- **THEN** 「保存」按钮为 disabled 状态

#### Scenario: 两次新密码一致后仍须满足复杂度

- **GIVEN** 用户输入的当前密码非空
- **WHEN** 新密码与确认新密码相同但不满足复杂度
- **THEN** 「保存」按钮保持 disabled

#### Scenario: 满足条件后启用保存

- **GIVEN** 用户输入的当前密码非空
- **WHEN** 新密码与确认新密码相同且满足复杂度
- **THEN** 「保存」按钮变为可点击

### Requirement: 前台头像展示刷新与 cache-bust

前台脚本在渲染侧栏用户头像（`#frontUserMenuBtn`）与个人资料头像预览（`#profileAvatarPreview`）时，若使用 `avatar_url`，SHALL 追加 cache-bust 查询参数（基于用户 `updated_at` 或上传成功时刻），以避免覆盖上传同一对象键后浏览器仍显示旧图。头像上传成功或 `loadAuthMe()` 后 MUST 立即刷新上述两处展示。

#### Scenario: 上传头像后侧栏更新

- **GIVEN** 用户在前台个人资料中上传并保存头像成功
- **WHEN** 保存完成
- **THEN** 侧栏 `#frontUserMenuBtn` 显示新头像图片

#### Scenario: 上传头像后弹层预览更新

- **GIVEN** 用户在前台个人资料中上传并保存头像成功
- **WHEN** 保存完成且弹层仍打开或再次打开
- **THEN** `#profileAvatarPreview` 显示新头像图片
