---
req_id: REQ-0016-external-integrations
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/external-integrations/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：外部集成边界治理。

# 原始描述
基于项目内已生效规格 `openspec/specs/external-integrations/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/external-integrations/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义本系统**出站外部集成**能力的规范范围。**当前版本不包含**任何第三方 HTTP 工作流或元数据 AI 建议代理。对象存储（S3 兼容）的上传、读取、生命周期与错误形态由「歌曲文件与对象存储生命周期」等规范从业务侧描述；对象存储仍属外部依赖，但不在本文件中重复其数据面细则。
