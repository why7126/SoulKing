---
req_id: REQ-0008-song-lyrics
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/song-lyrics/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：LRC 歌词管理与播放展示。

# 原始描述
基于项目内已生效规格 `openspec/specs/song-lyrics/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/song-lyrics/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「歌曲 LRC 歌词」能力：将 `.lrc` 作为歌曲附属 `SongFile` 入库与存储、按歌曲读取/上传/删除歌词、解析 LRC 时间标签，以及与试听/下载音频变体的隔离。本规范描述当前已实现行为。
