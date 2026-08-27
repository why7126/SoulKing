---
req_id: REQ-0001-application-auth
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/application-auth/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：应用认证与会话管理。

# 原始描述
基于项目内已生效规格 `openspec/specs/application-auth/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/application-auth/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义应用层身份鉴别与会话：用户名密码登录、HttpOnly Cookie 会话、角色（`admin`/`user`）、密码复杂度、公开端点白名单，以及禁用用户立即失效会话。
