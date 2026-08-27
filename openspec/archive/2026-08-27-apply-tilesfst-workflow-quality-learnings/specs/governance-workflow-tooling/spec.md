## MODIFIED Requirements

### Requirement: 治理上下文预算

本项目 MUST 通过规则和脚本约束 Agent 的读取范围、摘要复用、宽泛搜索和命令输出契约。

#### Scenario: 命令最终输出契约卫生

- **WHEN** 命令技能定义最终输出契约
- **THEN** 技能 MUST 要求最终回复输出真实结果
- **AND** 不得给出可被原样复制的尖括号占位模板、与当前命令无关的通用示例或 `MUST` / `SHOULD` 规范语气
- **AND** `scripts/validate-agent-context-budget.py` MUST 拦截最终输出占位模板、通用 BUG 示例、重复诱因和规范语气泄漏风险

### Requirement: Agent 治理命令必须提供可校验的流程门禁

Agent 治理命令 MUST 通过项目规则、技能文档和校验脚本约束命令顺序、Sprint Inclusion Gate、上下文预算、学习对象只读保护、Git 安全检查和最终输出契约。

#### Scenario: Sprint 选择与连续编号门禁

- **WHEN** `/sprint-propose` 选择或创建 Sprint
- **THEN** 命令 SHOULD 先运行 `python scripts/validate-sprint-selection.py [--sprint <sprint-id>]`
- **AND** 未指定 Sprint 时 MUST 按 active Sprint 数量选择、默认当前 Sprint 或阻断
- **AND** 新建 Sprint MUST 使用最大规范编号加一
- **AND** 已存在两个 active Sprint 时 MUST 阻断创建第三个 active Sprint

#### Scenario: Sprint 人读规划源一致性

- **WHEN** `/sprint-propose` 新建、追加或修正 Sprint 正式范围
- **THEN** 命令 MUST 以 `sprint.yaml` 作为机器事实源
- **AND** 必须通过 Workflow Sync 刷新 `sprint.md`、`release-note.md`、`acceptance-report.md`、Issue trace 和 Change trace
- **AND** `python scripts/validate-sprint-scope.py <sprint-id> [--item <id>]` MUST 校验 `sprint.md` `## 1. 目标` 编号列表、`## 2. Scope` 六列主表和派生 Scope 表均包含正式范围
- **AND** `## 2. Scope` 主表 MUST 保持 `类型 | 编号 | 标题 | 状态 | 估算 | 说明` 六列

#### Scenario: Sprint 归档 stale scan

- **WHEN** `/sprint-archive` 关闭 Sprint
- **THEN** archive readiness MUST 执行 Sprint close stale scan
- **AND** 四件套和 scoped REQ/BUG 子文档不得残留与真实生命周期冲突的待命令、待实现、待验收、active Change 路径或 legacy archive canonical 路径
- **AND** 10 个及以上 Change 的 Sprint MUST 优先检查 `change_batches` 摘要，再读取必要原始 Change 文档

#### Scenario: BUG review confirmed 根因门禁

- **WHEN** `/bug-review <BUG-full-id>` 走默认 approve 或显式 approve 路径
- **THEN** 命令 MUST 运行 `python scripts/validate-root-cause-evidence.py --bug <BUG-id> --require-confirmed`
- **AND** `unknown`、`hypothesis`、`probable`、缺少 `root-cause.md` 或缺少根因状态均 MUST 阻断 approve
- **AND** confirmed 根因缺少可定位证据链时 MUST 阻断 approve

#### Scenario: AI Usage 矩阵 unknown 语义

- **WHEN** Sprint Fact Sheet 输出 AI Usage 矩阵
- **THEN** 原始矩阵列状态 MUST 区分 `observed` 与 `unknown`
- **AND** 用户可见矩阵 MUST 将 `unknown` workflow 列渲染为 `-`
- **AND** `-` MUST 表示该 workflow 阶段未采集或未归因，不得等同于真实数字 `0`
- **AND** 只有 fresh gate、actual/present snapshot 和矩阵写入门禁均通过时，才可输出真实成本矩阵
