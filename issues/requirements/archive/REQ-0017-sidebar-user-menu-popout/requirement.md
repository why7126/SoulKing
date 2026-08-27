---
requirement_id: REQ-0017-sidebar-user-menu-popout
title: 收起侧栏用户菜单弹出布局
terminal: web-catalog
version: v1
status: archived
owner: product
source: openspec/specs/sidebar-user-menu-popout/spec.md
priority: P1
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
parent_requirement:
related_spec: sidebar-user-menu-popout
---

# 收起侧栏用户菜单弹出布局

## 背景
ProjectSoulKing 当前已在代码与已生效 OpenSpec 中实现 `sidebar-user-menu-popout` 能力。为避免需求状态只存在于对话或规格结果中，本需求将该能力回填到 `issues/requirements`，作为可审计的历史需求档案。

## 目标用户
- 个人音乐库维护者
- 管理员
- 已登录普通用户（适用于面向前台或账号自助的能力）

## 用户价值
定义侧边栏收起时底部用户头像下拉菜单的弹出布局：菜单须在窄轨道（64px）外侧向右浮出并保持中文菜单项横排可读；收起态菜单须在底部播放器/试听条之上完整可见可点；展开侧栏时保持既有侧栏内锚定行为；通过纯 CSS 实现，不改变菜单 HTML 与 JavaScript 开关逻辑。

## 范围 In
- 覆盖 `sidebar-user-menu-popout` 已生效规格中的 5 个 Requirement。
- 以当前代码、OpenSpec 与产品文档描述的已实现行为为准。
- 保留规格中的 Notes 与 Known Gaps 作为后续演进输入。

## 范围 Out
- 不在本需求中新增接口、数据结构、权限边界或 UI 行为。
- 不直接修改 `openspec/specs/`，仅引用其作为已生效事实源。
- 不承诺修复 Known Gaps；后续若处理需另建 REQ/BUG 与 OpenSpec Change。

## 功能要求
- FR-001：展开侧栏时用户菜单布局不变
- FR-002：收起态菜单最小可读宽度
- FR-003：纯样式实现且不改变菜单交互契约
- FR-004：收起侧栏时用户菜单左对齐用户头像上方弹出
- FR-005：收起侧栏时用户菜单与头像垂直间隙一致

## UI 约束
- 涉及前台或后台壳的能力，遵守 `ui-design.md` 与 `rules/ui-design.md` 的既有要求。
- 非 UI 能力不新增界面约束，以对应 OpenSpec 说明为准。

## 关联需求
- 关联规格：`openspec/specs/sidebar-user-menu-popout/spec.md`
- 关联归档 Change：
- `2026-05-25-align-collapsed-user-menu-avatar-gap`
- `2026-05-25-align-collapsed-user-menu-item-avatar`
- `2026-05-25-fix-collapsed-user-menu-player-overlap`
- `2026-05-25-fix-collapsed-user-menu-popout`

## Notes
当前规格未单独记录 Notes。

## Known Gaps
当前规格未单独记录 Known Gaps。

## 状态
- 当前状态：`archived`
- 归档原因：已实现能力的需求资产回填。
