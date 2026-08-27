---
requirement_id: REQ-0010-reference-data-taxonomy
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
source: requirement.md
---

# 验收标准

- AC-001：标签列表
- AC-002：标签创建
- AC-003：标签更新
- AC-004：标签删除
- AC-005：语言列表
- AC-006：语言创建
- AC-007：语言更新
- AC-008：语言删除
- AC-009：风格列表
- AC-010：风格创建
- AC-011：风格更新
- AC-012：风格删除
- AC-013：人物列表
- AC-014：人物创建
- AC-015：人物更新
- AC-016：人物删除

## 通用验收
- [x] `openspec/specs/reference-data-taxonomy/spec.md` 已存在并作为已生效能力事实源。
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
| `docs/knowledge-base/README.md` | not_applicable | 当前知识库无针对 `reference-data-taxonomy` 的专项条目 |
