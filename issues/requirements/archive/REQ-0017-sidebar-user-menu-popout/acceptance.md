---
requirement_id: REQ-0017-sidebar-user-menu-popout
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
source: requirement.md
---

# 验收标准

- AC-001：展开侧栏时用户菜单布局不变
- AC-002：收起态菜单最小可读宽度
- AC-003：纯样式实现且不改变菜单交互契约
- AC-004：收起侧栏时用户菜单左对齐用户头像上方弹出
- AC-005：收起侧栏时用户菜单与头像垂直间隙一致

## 通用验收
- [x] `openspec/specs/sidebar-user-menu-popout/spec.md` 已存在并作为已生效能力事实源。
- [x] 项目文档中保留该能力的产品、API、数据或存储说明（如适用）。
- [x] 本需求未引入新的代码行为变更。

## 测试策略
- 以 OpenSpec 中每个 Scenario 作为回归用例来源。
- 涉及 API 的能力通过 FastAPI `/docs`、接口调用或集成测试验证。
- 涉及 UI 的能力通过前后台静态壳手工或浏览器自动化验证。
- 涉及对象存储的能力需覆盖 MinIO 可用、对象缺失和路径迁移场景。

## Knowledge Gate

| 来源 | 适用性 | 写入位置 |
|---|---|---|
| `docs/knowledge-base/README.md` | not_applicable | 当前知识库无针对 `sidebar-user-menu-popout` 的专项条目 |
