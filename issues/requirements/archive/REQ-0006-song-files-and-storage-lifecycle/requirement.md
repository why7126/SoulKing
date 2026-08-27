---
requirement_id: REQ-0006-song-files-and-storage-lifecycle
title: 歌曲文件与对象存储生命周期
terminal: multi
version: v1
status: archived
owner: product
source: openspec/specs/song-files-and-storage-lifecycle/spec.md
priority: P1
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
parent_requirement:
related_spec: song-files-and-storage-lifecycle
---

# 歌曲文件与对象存储生命周期

## 背景
ProjectSoulKing 当前已在代码与已生效 OpenSpec 中实现 `song-files-and-storage-lifecycle` 能力。为避免需求状态只存在于对话或规格结果中，本需求将该能力回填到 `issues/requirements`，作为可审计的历史需求档案。

## 目标用户
- 个人音乐库维护者
- 管理员
- 已登录普通用户（适用于面向前台或账号自助的能力）

## 用户价值
定义「歌曲文件与对象存储生命周期」能力：向已有歌曲追加音频文件、修改展示用文件名并触发存储键调整、删除单条文件及其对象、按歌曲批量同步存储路径，以及按文件标识从对象存储读取（流式含分段）与附件下载。本规范仅描述当前已实现行为；与扫描入库、纯元数据保存触发搬迁的交界见 Notes。

## 范围 In
- 覆盖 `song-files-and-storage-lifecycle` 已生效规格中的 9 个 Requirement。
- 以当前代码、OpenSpec 与产品文档描述的已实现行为为准。
- 保留规格中的 Notes 与 Known Gaps 作为后续演进输入。

## 范围 Out
- 不在本需求中新增接口、数据结构、权限边界或 UI 行为。
- 不直接修改 `openspec/specs/`，仅引用其作为已生效事实源。
- 不承诺修复 Known Gaps；后续若处理需另建 REQ/BUG 与 OpenSpec Change。

## 功能要求
- FR-001：向已有歌曲追加音频文件
- FR-002：修改展示用文件名并同步存储路径
- FR-003：删除单条音频文件
- FR-004：按歌曲同步存储路径
- FR-005：对象键的计算与全局唯一性
- FR-006：按文件标识流式读取与附件下载
- FR-007：向已有歌曲上传歌词文件
- FR-008：删除歌词文件记录
- FR-009：音频与歌词对象存储桶

## UI 约束
- 涉及前台或后台壳的能力，遵守 `ui-design.md` 与 `rules/ui-design.md` 的既有要求。
- 非 UI 能力不新增界面约束，以对应 OpenSpec 说明为准。

## 关联需求
- 关联规格：`openspec/specs/song-files-and-storage-lifecycle/spec.md`
- 关联归档 Change：
- `2026-05-26-add-lyrics-support`
- `2026-05-29-consolidate-minio-single-soulking-bucket`

## Notes
- 允许上传与追加的音频后缀集合由应用侧固定配置，与扫描入库使用同一集合。
- 保存歌曲元数据、合并所选歌曲等其它流程也可能在提交前触发同一套「按歌曲同步存储路径」逻辑；本条规范在「单文件与按歌曲管理」接口处展开，其它入口不在此重复列举路由。
- 公开接口文档或模型注释中若存在「仅改展示名、不改存储路径」之类表述，与当前改名接口在保存后触发路径同步的实现可能不一致；以运行行为为准。
- 流式读取接口以文件记录存在为前提，不要求另行校验父歌曲是否存在；附件下载接口额外要求父歌曲记录存在。

## Known Gaps
以下为未以强制性语句全文承诺的行为：

- **分段搬迁**：某一文件的桶内复制失败时，实现可能跳过该条并继续处理其它文件，导致同一歌曲下部分记录已指向新键、部分仍为旧键；是否需人工再次「同步存储路径」取决于此时数据状态。
- **删除顺序**：先删对象再删记录；对象删除失败仍删除记录时，可能在桶中残留无法通过本条记录访问的对象。
- **并发**：未在同一规范中约束多请求同时搬迁同一歌曲时的互斥。
- **前端**：上传、改名、删除、同步路径在浏览器中的交互与错误展示未约束。
- **数据不一致**：若存在「文件记录指向已删除歌曲」的异常数据，流式接口仍可能尝试按键拉取对象，行为取决于对象是否仍存在；附件下载会因父歌曲校验而失败。

## 状态
- 当前状态：`archived`
- 归档原因：已实现能力的需求资产回填。
