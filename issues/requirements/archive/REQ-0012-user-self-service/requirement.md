---
requirement_id: REQ-0012-user-self-service
title: 前台用户自助资料维护
terminal: web-catalog
version: v1
status: archived
owner: product
source: openspec/specs/user-self-service/spec.md
priority: P1
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
parent_requirement:
related_spec: user-self-service
---

# 前台用户自助资料维护

## 背景
ProjectSoulKing 当前已在代码与已生效 OpenSpec 中实现 `user-self-service` 能力。为避免需求状态只存在于对话或规格结果中，本需求将该能力回填到 `issues/requirements`，作为可审计的历史需求档案。

## 目标用户
- 个人音乐库维护者
- 管理员
- 已登录普通用户（适用于面向前台或账号自助的能力）

## 用户价值
定义当前登录用户在前台壳内自助维护账号资料的能力：昵称、用户名、密码与头像；不包含管理员代管他人资料。

## 范围 In
- 覆盖 `user-self-service` 已生效规格中的 4 个 Requirement。
- 以当前代码、OpenSpec 与产品文档描述的已实现行为为准。
- 保留规格中的 Notes 与 Known Gaps 作为后续演进输入。

## 范围 Out
- 不在本需求中新增接口、数据结构、权限边界或 UI 行为。
- 不直接修改 `openspec/specs/`，仅引用其作为已生效事实源。
- 不承诺修复 Known Gaps；后续若处理需另建 REQ/BUG 与 OpenSpec Change。

## 功能要求
- FR-001：修改个人资料
- FR-002：修改密码
- FR-003：上传头像
- FR-004：前台用户菜单接入自助能力

## UI 约束
- 涉及前台或后台壳的能力，遵守 `ui-design.md` 与 `rules/ui-design.md` 的既有要求。
- 非 UI 能力不新增界面约束，以对应 OpenSpec 说明为准。

## 关联需求
- 关联规格：`openspec/specs/user-self-service/spec.md`
- 关联归档 Change：
- `2026-05-28-add-user-auth-system`
- `2026-05-28-align-profile-password-ui-with-studio-design`
- `2026-05-28-fix-profile-avatar-password-ux`
- `2026-05-29-add-password-show-hide-toggle`
- `2026-05-29-consolidate-minio-single-soulking-bucket`
- `2026-05-29-fix-avatar-presigned-display`

## Notes
当前规格未单独记录 Notes。

## Known Gaps
当前规格未单独记录 Known Gaps。

## 状态
- 当前状态：`archived`
- 归档原因：已实现能力的需求资产回填。
