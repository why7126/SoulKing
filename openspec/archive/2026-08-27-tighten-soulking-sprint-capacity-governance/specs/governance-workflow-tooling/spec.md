## ADDED Requirements

### Requirement: Sprint 容量门禁

本项目 SHALL 在 Sprint 提议和正式范围追加阶段计算容量占用率，并根据容量区间决定是否通过、风险通过或硬阻断。

#### Scenario: 新建 Sprint 使用项目默认容量基线

- **WHEN** `/sprint-propose` 创建新的 Sprint
- **AND** `project.yaml` 配置了 `ai.sprint_capacity.capacity_person_days`
- **THEN** 系统 MUST 默认使用该值作为新 Sprint 的 `capacity_person_days`
- **AND** `sprint.yaml.capacity_gate.capacity_person_days` MUST 与该容量基线保持一致

#### Scenario: 容量不超过计划基线时正常通过

- **WHEN** `/sprint-propose` 或范围追加评估候选范围
- **AND** `estimated_person_days <= capacity_person_days`
- **THEN** 系统 MUST 按既有 Review Gate、Readiness Gate、Sprint Selection Gate 和 Scope Gate 继续
- **AND** `capacity_gate.result` MUST 记录为 `pass`

#### Scenario: 容量超过 100% 且不超过 120% 时风险通过

- **WHEN** `/sprint-propose` 或范围追加评估候选范围
- **AND** `capacity_person_days < estimated_person_days <= capacity_person_days * 1.2`
- **THEN** 系统 MAY 继续生成或更新 Sprint 正式范围
- **AND** Sprint 文档 MUST 记录容量风险、fix 缓冲影响和延后项建议
- **AND** `capacity_gate.result` MUST 记录为 `pass_with_risk`

#### Scenario: 容量超过 120% 时硬阻断

- **WHEN** `/sprint-propose` 或范围追加评估候选范围
- **AND** `estimated_person_days > capacity_person_days * 1.2`
- **THEN** 系统 MUST 阻断正式规划写入
- **AND** 系统 MUST NOT 生成 `iterations/change/<sprint>/` 四件套
- **AND** 系统 MUST NOT 更新 REQ、BUG 或 Change trace 的 Sprint 关联
- **AND** 系统 MUST 提示拆分 Sprint、移出低优先级项或替换范围后重新评估
- **AND** `capacity_gate.result` MUST 记录为 `blocked`，如果候选数据已经进入临时评估对象

#### Scenario: 容量字段缺失时不得默认通过

- **WHEN** `/sprint-propose` 或范围追加无法获得 `capacity_person_days` 或 `estimated_person_days`
- **THEN** 系统 MUST 停止容量门禁
- **AND** 系统 MUST 提示先补齐容量或估算输入

#### Scenario: sprint.yaml 保存容量门禁字段

- **WHEN** Sprint 正式范围被创建、追加或修正
- **THEN** `sprint.yaml` MUST 记录 `capacity_person_days`、`estimated_person_days`、`capacity_usage`、`fix_buffer_person_days`、`fix_buffer_ratio` 和 `capacity_gate`
- **AND** `capacity_gate` MUST 至少包含 `capacity_person_days`、`estimated_person_days`、`capacity_usage`、`result` 和 `note`
