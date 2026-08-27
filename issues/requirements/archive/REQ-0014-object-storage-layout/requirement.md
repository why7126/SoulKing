---
requirement_id: REQ-0014-object-storage-layout
title: MinIO 单桶对象存储布局
terminal: multi
version: v1
status: archived
owner: product
source: openspec/specs/object-storage-layout/spec.md
priority: P1
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
parent_requirement:
related_spec: object-storage-layout
---

# MinIO 单桶对象存储布局

## 背景
ProjectSoulKing 当前已在代码与已生效 OpenSpec 中实现 `object-storage-layout` 能力。为避免需求状态只存在于对话或规格结果中，本需求将该能力回填到 `issues/requirements`，作为可审计的历史需求档案。

## 目标用户
- 个人音乐库维护者
- 管理员
- 已登录普通用户（适用于面向前台或账号自助的能力）

## 用户价值
定义全项目唯一的 MinIO/S3 对象存储桶（默认 `soulking`）、桶内目录前缀（音频/歌词、头像、`covers/`）及自双桶架构迁移的存量数据要求。

## 范围 In
- 覆盖 `object-storage-layout` 已生效规格中的 3 个 Requirement。
- 以当前代码、OpenSpec 与产品文档描述的已实现行为为准。
- 保留规格中的 Notes 与 Known Gaps 作为后续演进输入。

## 范围 Out
- 不在本需求中新增接口、数据结构、权限边界或 UI 行为。
- 不直接修改 `openspec/specs/`，仅引用其作为已生效事实源。
- 不承诺修复 Known Gaps；后续若处理需另建 REQ/BUG 与 OpenSpec Change。

## 功能要求
- FR-001：单一对象存储桶
- FR-002：桶内目录前缀约定
- FR-003：MinIO 存量迁移

## UI 约束
- 涉及前台或后台壳的能力，遵守 `ui-design.md` 与 `rules/ui-design.md` 的既有要求。
- 非 UI 能力不新增界面约束，以对应 OpenSpec 说明为准。

## 关联需求
- 关联规格：`openspec/specs/object-storage-layout/spec.md`
- 关联归档 Change：
- `2026-05-29-consolidate-minio-single-soulking-bucket`

## Notes
当前规格未单独记录 Notes。

## Known Gaps
当前规格未单独记录 Known Gaps。

## 状态
- 当前状态：`archived`
- 归档原因：已实现能力的需求资产回填。
