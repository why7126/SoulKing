---
req_id: REQ-0004-music-ingestion
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/music-ingestion/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：音乐扫描上传与入库。

# 原始描述
基于项目内已生效规格 `openspec/specs/music-ingestion/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/music-ingestion/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「音乐入库」能力：从本地目录递归扫描符合格式的音频文件，或通过上传接口接收多个音频文件，将其写入对象存储并在曲库中建立或关联歌曲与专辑记录；同时提供一次操作范围内的进度与跳过说明查询能力。本规范仅描述当前已实现行为。
