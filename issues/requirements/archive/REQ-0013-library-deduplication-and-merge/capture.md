---
req_id: REQ-0013-library-deduplication-and-merge
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/library-deduplication-and-merge/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：曲库去重与合并治理。

# 原始描述
基于项目内已生效规格 `openspec/specs/library-deduplication-and-merge/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/library-deduplication-and-merge/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「曲库去重与合并」能力：在服务端按既定规则将多条曲目记录合并为一条「主曲目」，把重复曲目下的音频文件归属与关联数据迁到主曲目，并删除被合并掉的曲目记录；提供启动时一次性迁移、后台再次自动合并，以及后台按勾选指定主曲目的合并入口。本规范仅描述当前已实现行为；**入库/扫描阶段基于文件内容或哈希的重复跳过**属于另一条链路，不在此展开。
