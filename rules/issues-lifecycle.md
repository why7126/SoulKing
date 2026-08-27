---
purpose: Issue 生命周期
content: 需求和 BUG 从捕获、评审到归档的阶段规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-10 23:20:00
---

# Issue 生命周期

需求目录：`issues/requirements/{plan,review,archive}/REQ-*`。

BUG 目录：`issues/bugs/{plan,review,archive}/BUG-*`。

阶段规则：

- `plan`：捕获、拆分、补充上下文。
- `review`：完成验收标准、影响面、测试策略并等待评审。
- `archive`：对应 Change 和 Sprint 完成后归档。

未评审或未批准的 REQ/BUG 不得进入 Sprint 正式范围，不得转 OpenSpec 实现。

## 当前态看板索引

`issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md` SHOULD 维护每个 Issue 一行的当前态快照，覆盖当前状态、阶段、关联 Sprint、关联 Change、最近更新时间、下一步和事实源路径。

当前态看板索引不参与机器状态判断；脚本、Agent 和人工评审 MUST 继续以 `_registry.yaml`、单条 Issue `trace.md`、Sprint 四件套和 OpenSpec Change 为事实源。新增或更新当前态行时 MUST 使用 `YYYY-MM-DD HH:mm:ss`，并不得写入隐私、密钥、未脱敏日志、本机绝对路径或真实用户数据。
