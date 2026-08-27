---
req_id: REQ-0014-object-storage-layout
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/object-storage-layout/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：MinIO 单桶对象存储布局。

# 原始描述
基于项目内已生效规格 `openspec/specs/object-storage-layout/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/object-storage-layout/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义全项目唯一的 MinIO/S3 对象存储桶（默认 `soulking`）、桶内目录前缀（音频/歌词、头像、`covers/`）及自双桶架构迁移的存量数据要求。
