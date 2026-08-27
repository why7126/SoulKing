---
req_id: REQ-0010-reference-data-taxonomy
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/reference-data-taxonomy/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：参考数据与分类体系管理。

# 原始描述
基于项目内已生效规格 `openspec/specs/reference-data-taxonomy/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/reference-data-taxonomy/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「参考数据 / 分类体系」能力：通过服务端接口维护四类可控词汇——**标签**、**语言**、**风格**、**人物（艺人）**——的查询与增删改；并说明删除时对曲目关联数据的处理方式。人物除名称外还支持一组类型标签的读写。本规范仅描述当前已实现行为；曲目如何引用这些参考数据属于曲目元数据能力，不在此展开字段语义。
