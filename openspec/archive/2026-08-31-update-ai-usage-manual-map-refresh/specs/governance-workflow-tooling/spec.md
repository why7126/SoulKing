## ADDED Requirements

### Requirement: AI Usage manual map 恢复流程

本项目 SHALL 为 AI Usage `estimated_fallback`、snapshot 缺失、过期、失败或覆盖不足场景提供可复验的 manual map 恢复流程，并通过 Sprint Fact Sheet 门禁防止 fallback 结果被误当真实 token 统计。

#### Scenario: manual map 字段和键选择说明

- **WHEN** 操作者查看 `scripts/extract-ai-usage.py --help` 或相邻操作说明
- **THEN** 系统 MUST 描述 `--manual-map` 的适用场景、键选择和字段集合
- **AND** manual map MUST 支持以 `turn_hash` 或 `source_session_hash` 作为映射键
- **AND** manual map MUST 支持 `requirements`、`bugs`、`changes`、`sprint_id`、`workflow_event`、`release_sprints`、`release_version`、`post_command_target` 和 `attribution_confidence`

#### Scenario: 使用本地 session 与 manual map 刷新 Sprint snapshot

- **WHEN** 操作者同时提供本地 session JSONL、manual map 和 `--sprint <sprint-id>`
- **THEN** `scripts/extract-ai-usage.py` MUST 生成或更新 `data/ai-usage/sprints/<sprint-id>.json`
- **AND** 输出 MUST 保留 `status`、`usage_mode`、`command_run_count`、`sprint_snapshot`、`warning_count` 和 `recommended_action` 摘要
- **AND** 输出和派生产物 MUST NOT 持久化原始 session JSONL、prompt、系统/开发者指令、本机绝对路径、密钥、Cookie、Authorization header、`.env` 内容或完整工具输出

#### Scenario: 刷新后复查 Fact Sheet summary

- **WHEN** Sprint snapshot 被 manual map 刷新
- **THEN** 操作者 MUST 重新运行 Fact Sheet summary
- **AND** 复查 MUST 使用刷新后的 `fresh_gate`、`snapshot_status`、`ai_usage_mode`、coverage、totals 和 `usage_matrices_summary`
- **AND** 系统 MUST NOT 沿用刷新前的 fallback、missing、stale 或 failed 结论

#### Scenario: 真实 token 矩阵写入门禁

- **WHEN** 操作者请求生成 AI Usage token 矩阵
- **THEN** 系统 MUST 仅在 snapshot present、usage mode actual、fresh gate pass 且矩阵写入门禁通过时输出真实 token 矩阵
- **AND** 当 workflow 阶段未采集或未归因时，用户可见矩阵 MUST 使用 `-` 表示 unknown，不得渲染为真实数字 `0`
- **AND** 当 session JSONL 缺失、路径不可用、缺少 token_count 事件、coverage 不足或矩阵缺失时，系统 MUST 输出明确 `recommended_action` 并阻止默认写入真实 token 成本矩阵

#### Scenario: Sprint archive 与 Sprint exps 使用恢复分支

- **WHEN** `/sprint-archive` 或 `/sprint-exps` 发现 AI Usage snapshot missing、stale、failed、fallback 或 coverage blocker
- **THEN** 命令说明 MUST 提供 manual map 恢复分支
- **AND** 恢复分支 MUST 包含提供 session JSONL、提供 manual map、刷新 sprint snapshot、重新生成 Fact Sheet summary 和重新判断 token 矩阵门禁
- **AND** 命令 MUST NOT 手工估填 token 数字或把 `estimated_fallback` 伪装为真实统计
