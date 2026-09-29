## 1. AI Usage manual map 输入与刷新

- [x] 1.1 补充 `scripts/extract-ai-usage.py --help` 或相邻说明，描述 `--manual-map` 的适用场景、`turn_hash` 与 `source_session_hash` 键选择和字段集合。
- [x] 1.2 确认 manual map 合并逻辑覆盖 `requirements`、`bugs`、`changes`、`sprint_id`、`workflow_event`、`release_sprints`、`release_version`、`post_command_target` 和 `attribution_confidence`。
- [x] 1.3 确认 `--session-jsonl`、`--manual-map` 与 `--sprint` 组合会生成或刷新 `data/ai-usage/sprints/<sprint-id>.json`，并输出紧凑 hook 摘要。

## 2. Fact Sheet 与矩阵门禁

- [x] 2.1 更新 Fact Sheet summary 复查说明或实现，要求刷新后重新读取 `fresh_gate`、`snapshot_status`、`ai_usage_mode`、coverage、totals 与 `usage_matrices_summary`。
- [x] 2.2 确认 `--ai-usage-markdown` 仅在 snapshot present、usage mode actual、fresh gate pass 且矩阵写入门禁通过时输出真实 token 矩阵。
- [x] 2.3 确认 missing、stale、failed、fallback、coverage blocker 或矩阵缺失时输出明确 `recommended_action`，且不写真实 token 成本矩阵。

## 3. Sprint 命令说明与安全边界

- [x] 3.1 更新 `/sprint-archive` 技能说明，加入 manual map 恢复分支。
- [x] 3.2 更新 `/sprint-exps` 技能说明，加入 manual map 恢复分支。
- [x] 3.3 确认 AI Usage 输入、输出、命令摘要和长期文档不会持久化原始 session、prompt、系统/开发者指令、本机绝对路径、密钥、Cookie、Authorization header、`.env` 内容或完整工具输出。

## 4. 验证

- [x] 4.1 增加或更新聚焦测试，覆盖 manual map 字段合并、键匹配、`post_command_target` 选择和归因置信度默认值。
- [x] 4.2 增加或更新命令级测试，覆盖 `--session-jsonl` + `--manual-map` + `--sprint` 刷新 snapshot 的成功路径。
- [x] 4.3 增加或更新 Fact Sheet 测试，覆盖 fresh gate 通过时矩阵可写，以及 blocker/fallback 时矩阵不可写。
- [x] 4.4 运行 OpenSpec、产品数据观测门禁、Workflow Sync 和相关 pytest 聚焦验证。
