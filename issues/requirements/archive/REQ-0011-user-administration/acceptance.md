---
requirement_id: REQ-0011-user-administration
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
source: requirement.md
---

# 验收标准

- AC-001：仅管理员可管理用户
- AC-002：列出用户
- AC-003：创建用户
- AC-004：更新用户
- AC-005：禁止禁用管理员账号
- AC-006：种子管理员启动自愈
- AC-007：PATCH 用户端点 HTTP 可达
- AC-008：软删除用户
- AC-009：重置他人密码
- AC-010：后台用户管理界面

## 通用验收
- [x] `openspec/specs/user-administration/spec.md` 已存在并作为已生效能力事实源。
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
| `docs/knowledge-base/README.md` | not_applicable | 当前知识库无针对 `user-administration` 的专项条目 |
