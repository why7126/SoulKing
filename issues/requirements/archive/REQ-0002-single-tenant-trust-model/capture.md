---
req_id: REQ-0002-single-tenant-trust-model
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/single-tenant-trust-model/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：单租户多账号信任模型。

# 原始描述
基于项目内已生效规格 `openspec/specs/single-tenant-trust-model/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/single-tenant-trust-model/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「单租户、多账号」安全与归属模型：同一部署实例使用**单一数据库连接**承载全部业务数据，曲库实体共享、歌单等按用户归属；应用层对业务 API 须会话鉴权，管理端点须管理员角色。传输加密、网络隔离、反向代理鉴权等若存在则属于部署环境，不在此承诺。
