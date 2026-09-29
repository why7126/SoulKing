---
requirement_id: REQ-0018-ai-usage-manual-map-refresh
acceptance_status: passed
created_at: 2026-08-31 08:59:00
updated_at: 2026-08-31 10:23:00
source: requirement.md
---

# 验收标准

- [ ] AC-001：`scripts/extract-ai-usage.py --help` 或相邻操作说明清楚描述 `--manual-map` 的适用场景、键选择和字段集合。
- [ ] AC-002：manual map 支持以 `turn_hash` 或 `source_session_hash` 作为键，并能合并 `requirements`、`bugs`、`changes`、`sprint_id`、`workflow_event`、`release_sprints`、`release_version`、`post_command_target` 与 `attribution_confidence`。
- [ ] AC-003：给定本地 session JSONL 与 manual map 后，刷新命令能生成或更新 `data/ai-usage/sprints/<sprint-id>.json`。
- [ ] AC-004：刷新后必须重新运行 Fact Sheet summary，并以刷新后的 `fresh_gate`、`snapshot_status`、`ai_usage_mode`、coverage、totals 和 `usage_matrices_summary` 判断是否可输出矩阵。
- [ ] AC-005：只有 snapshot present、usage mode actual、fresh gate pass 且矩阵写入门禁通过时，才允许通过 `--ai-usage-markdown` 生成真实 token 矩阵。
- [ ] AC-006：session JSONL 缺失、路径不可用、缺少 token_count 事件、覆盖不足或矩阵缺失时，命令输出明确 `recommended_action`，且不写真实 token 成本矩阵。
- [ ] AC-007：`/sprint-archive` 与 `/sprint-exps` 说明包含 manual map 恢复分支，减少 Sprint 关闭后再返工刷新。
- [ ] AC-008：AI Usage 输入、输出、命令摘要和长期文档不得持久化原始 session、prompt、系统/开发者指令、本机绝对路径、密钥、Cookie、Authorization header、`.env` 内容或完整工具输出。

## 通用验收
- [ ] 需求实现前已纳入 Sprint scope，并通过对应 `/req-opsx` 创建 OpenSpec Change。
- [ ] 实现后同步相关命令技能说明、长期文档或脚本帮助，确保下一命令可消费该流程。
- [ ] 相关验证命令输出只保留摘要，不展开原始 session JSONL、prompt、工具输出或本机绝对路径。

## 测试策略
- 单元测试覆盖 manual map 的字段合并、键匹配、`post_command_target` 选择与归因置信度默认值。
- 命令级测试覆盖 `--session-jsonl` + `--manual-map` + `--sprint` 刷新 snapshot 的成功路径。
- Fact Sheet 测试覆盖刷新后 `fresh_gate=pass` 时矩阵可写，以及 blocker/fallback 时矩阵不可写。
- 负向测试覆盖 session 缺失、token_count 缺失、coverage 不足、矩阵缺失和安全记录被跳过时的 `recommended_action`。
- 安全测试覆盖不会把原始 session、prompt、系统/开发者指令、本机绝对路径、密钥、Cookie、Authorization header、`.env` 内容或完整工具输出写入仓库产物。

## 产品数据采集与链路观测
product_data_collection_observability:
- status = not_applicable
- reason: 本需求只影响仓库内 AI Agent 治理统计流程和 `data/ai-usage` 派生产物，不改变 SoulKing 产品侧 API、数据库、请求日志、行为事件、Task Trace、前台请求封装、后台请求封装、媒体链路或对象存储读写。
- affected_layers: []
- validation: 已读取 `docs/standards/product-data-collection-observability.md` 并复核适用范围；后续实现阶段通过聚焦校验确认未引入产品侧采集或链路观测变更。

## Knowledge Gate

| 来源 | 适用性 | 写入位置 |
|---|---|---|
| `docs/knowledge-base/README.md` | not_applicable | 本需求无 UI 场景标签，无横切 AC |
| `docs/knowledge-base/retrospectives/sprint-001-retrospective.md` | applicable | AC-001 至 AC-008，来源于 T-003 与 AI Usage 复盘经验 |

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-31 10:23:00
accepted_by: workflow-sync
source_change: update-ai-usage-manual-map-refresh
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

