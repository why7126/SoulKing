---
req_id: REQ-0006-song-files-and-storage-lifecycle
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/song-files-and-storage-lifecycle/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：歌曲文件与对象存储生命周期。

# 原始描述
基于项目内已生效规格 `openspec/specs/song-files-and-storage-lifecycle/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/song-files-and-storage-lifecycle/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「歌曲文件与对象存储生命周期」能力：向已有歌曲追加音频文件、修改展示用文件名并触发存储键调整、删除单条文件及其对象、按歌曲批量同步存储路径，以及按文件标识从对象存储读取（流式含分段）与附件下载。本规范仅描述当前已实现行为；与扫描入库、纯元数据保存触发搬迁的交界见 Notes。
