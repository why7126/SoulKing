---
req_id: REQ-0009-playlist-management
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/playlist-management/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：歌单管理。

# 原始描述
基于项目内已生效规格 `openspec/specs/playlist-management/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/playlist-management/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「歌单管理」能力：通过服务端接口维护歌单集合（列表、创建、重命名、删除、整体排序），维护歌单内曲目条目（按顺序展示、追加、移除），并说明与删除曲目、合并曲目相关的歌单条目联动。歌单详情中每条可解析曲目返回的概要信息与曲库浏览列表接口中的曲目条目同属一类概要形态；字段语义与多文件场景下的细微差异见 Known Gaps。
