---
purpose: OpenSpec 设计
content: TilesFST 工作流质量治理学习项的项目化设计
created_at: 2026-08-27 00:00:00
updated_at: 2026-08-27 01:30:00
---

# 设计：工作流质量治理学习项

## 决策

- 最终输出契约以 `.agents/skills/*/SKILL.md` 为命令事实源，`AGENTS.md` 和 `rules/agent-context-budget.md` 只保留入口摘要，`scripts/validate-agent-context-budget.py` 负责防回退。
- Sprint 选择使用独立轻量脚本读取 `iterations/change|archive/*/sprint.yaml`，避免命令执行时靠自然语言推断 active Sprint。
- `sprint.md` 同时作为产品可读规划源；`validate-sprint-scope.py` 必须校验 `## 1. 目标` 编号列表、`## 2. Scope` 六列主表和 workflow-sync 派生表，防止只更新机器 YAML 而遗漏人读规划。
- Sprint 归档 stale scan 优先阻断生命周期冲突事实；对已归档 Change，active path、`proposed` / `applied`、待实现、待验收等文案必须在关闭 Sprint 前清理。
- 大型 Sprint 归档先消费 readiness / Fact Sheet 的 `change_batches` 摘要，再按 blocker、warning、evidence hint 读取必要原始文件，避免为了归档队列无差别展开大量 Change 文档。
- BUG review approve 只在默认 approve 或显式 approve 路径要求 confirmed 根因；reject、defer、wont-fix 可继续记录非通过依据。
- AI Usage 原始数据保留 `unknown` 列状态，用户可见矩阵渲染为 `-`；真实数字 `0` 仅用于已观测 workflow 列。

## 影响面

- 治理规则：`AGENTS.md`、`rules/agent-context-budget.md`、`rules/iterations-lifecycle.md`、`rules/bug-management.md`、`rules/root-cause-evidence.md`
- 命令技能：`sprint-propose`、`bug-review`、`sprint-exps`、`req-opsx`、`bug-opsx`、`upgrade-plan`、`upgrade-validate`
- 脚本：上下文预算校验、Sprint selection、根因证据校验、AI Usage、Sprint Fact Sheet
- 测试：新增或更新对应聚焦测试

## 风险与控制

- 输出契约脚本可能暴露历史技能文件残留：通过先更新命令技能再运行校验控制。
- AI Usage snapshot 可能缺数据：以 fresh gate 和 matrix write gate 阻断真实矩阵输出，不估填 token。
- Sprint 当前已有历史治理项：新增 Change 通过 `sprint.yaml` 机器源纳入后再由 Workflow Sync 刷新派生文档。
