## REMOVED Requirements

### Requirement: 入站 HTTP 无应用层身份鉴别

**Reason**: 产品引入多账号与会话鉴权，业务 API 须登录；管理端点须管理员角色。

**Migration**: 客户端须先 `POST /auth/login` 获取会话 Cookie；自动化脚本配置测试账号。公开端点见 `application-auth`「公开端点」。

## ADDED Requirements

### Requirement: 单租户多账号与共享曲库

部署实例 SHALL 仍为单数据库连接、无租户标识字段；曲目、艺人、标签等曲库实体 MUST NOT 按用户分区，所有已登录用户 MUST 共享同一曲库视图。歌单等用户私有数据 MUST 通过 `user_id` 归属区分，不属于多租户隔离。

#### Scenario: 两用户看到相同歌曲列表

- **GIVEN** 用户 A 与用户 B 均已登录
- **WHEN** 二者分别请求同一筛选条件下的曲库列表 API
- **THEN** 返回的曲目集合一致（同一共享库）

#### Scenario: 歌单不跨用户可见

- **GIVEN** 用户 A 创建歌单
- **WHEN** 用户 B 请求歌单列表
- **THEN** 不包含用户 A 的歌单

### Requirement: 管理端点须应用层授权

`/admin/` 命名空间下的 API 与后台入口 SHALL 在应用层要求管理员角色；不得仅依赖网络可达性作为唯一保护。

#### Scenario: 未登录不可调用管理 API

- **GIVEN** 无会话
- **WHEN** 请求 `/admin/import-directory` 等
- **THEN** 返回 401

## MODIFIED Requirements

### Requirement: 无应用层多租户分区语义

业务数据模型与查询路径 MUST NOT 依赖「租户标识、组织标识」等字段对**曲库**做强制隔离；MUST NOT 在同一进程内按租户切分曲库。歌单、会话等用户级数据 MUST 通过 `user_id` 归属，不视为 SaaS 式多租户。

#### Scenario: 曲库访问不带租户维度

- **GIVEN** 库中存在曲目记录
- **WHEN** 已登录服务端列出或读写曲目
- **THEN** 不因租户 id 缺失而拒绝
- **AND** 不因用户 id 缺失而隐藏其他用户的曲目

#### Scenario: 歌单访问须匹配当前用户

- **GIVEN** 歌单属于用户 A
- **WHEN** 用户 B 请求该歌单详情
- **THEN** 返回未找到或 403/404（实现统一为一种）
