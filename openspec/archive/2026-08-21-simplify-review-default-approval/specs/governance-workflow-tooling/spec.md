## ADDED Requirements

### Requirement: REQ 和 BUG 评审命令默认通过

本项目 MUST 将无显式结果 flag 的 `/req-review <REQ-full-id>` 与 `/bug-review <BUG-full-id>` 解释为 `approve`，以降低常规评审通过路径的重复输入成本。

#### Scenario: 需求评审无 flag 默认批准

- **WHEN** 用户运行 `/req-review <REQ-full-id>` 且未提供 `--reject` 或 `--defer`
- **THEN** 命令 MUST 按 `approve` 结果执行
- **AND** MUST 生成或更新 `review.md`
- **AND** MUST 更新 `trace.md` 与 `requirement.md` 状态为 `approved`
- **AND** MUST 按批准路径执行目录迁移、Workflow Sync 与 AI Usage hook

#### Scenario: 缺陷评审无 flag 默认批准

- **WHEN** 用户运行 `/bug-review <BUG-full-id>` 且未提供 `--reject`、`--defer` 或 `--wont-fix`
- **THEN** 命令 MUST 按 `approve` 结果执行
- **AND** MUST 生成或更新 `review.md`
- **AND** MUST 更新相关 BUG 状态为 `approved`
- **AND** MUST 按批准路径执行目录迁移、Workflow Sync 与 AI Usage hook

#### Scenario: 非通过结论必须显式声明

- **WHEN** 用户希望评审结论为拒绝、延后或不修复
- **THEN** 命令 MUST 要求用户显式提供对应 flag
- **AND** `/req-review` MUST 仅接受 `--reject` 或 `--defer` 作为非通过结果
- **AND** `/bug-review` MUST 接受 `--reject`、`--defer` 或 `--wont-fix` 作为非通过结果

#### Scenario: 下一步提示省略常规 approve flag

- **WHEN** 命令、规则或文档推荐常规 REQ/BUG 评审通过路径
- **THEN** 下一步命令 SHOULD 使用 `/req-review <REQ-full-id>` 或 `/bug-review <BUG-full-id>`
- **AND** 不应在常规通过示例中继续要求 `--approve`
