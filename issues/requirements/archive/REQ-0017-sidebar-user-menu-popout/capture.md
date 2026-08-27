---
req_id: REQ-0017-sidebar-user-menu-popout
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/sidebar-user-menu-popout/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：收起侧栏用户菜单弹出布局。

# 原始描述
基于项目内已生效规格 `openspec/specs/sidebar-user-menu-popout/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/sidebar-user-menu-popout/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义侧边栏收起时底部用户头像下拉菜单的弹出布局：菜单须在窄轨道（64px）外侧向右浮出并保持中文菜单项横排可读；收起态菜单须在底部播放器/试听条之上完整可见可点；展开侧栏时保持既有侧栏内锚定行为；通过纯 CSS 实现，不改变菜单 HTML 与 JavaScript 开关逻辑。
