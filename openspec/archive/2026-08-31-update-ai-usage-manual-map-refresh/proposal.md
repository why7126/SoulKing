---
purpose: OpenSpec Change proposal
content: 固化 AI Usage manual map 与 Sprint snapshot 刷新流程
created_at: 2026-08-31 09:18:00
updated_at: 2026-08-31 09:18:00
---

# 固化 AI Usage manual map 与刷新流程

## 为什么

`sprint-001` 归档与复盘曾因缺少可用 session JSONL 或自动归因不足，使 AI Usage 以 `estimated_fallback` 进入关闭链路；后续依赖本地 session JSONL 与 manual map 手动补齐后，Sprint snapshot 才恢复为 `actual`。现有工具已有部分入口，但缺少可复验、可复制、可审计的恢复流程，容易在 Sprint archive、Sprint exps 和治理复盘中重复返工或误把 fallback 当作真实 token 统计。

## 变更内容

- 补充 `scripts/extract-ai-usage.py --manual-map` 的适用场景、键选择和字段语义说明。
- 固化 `--session-jsonl`、`--manual-map`、`--sprint` 的 snapshot 刷新链路，并要求刷新后重新复查 Fact Sheet summary。
- 强化真实 token 矩阵输出门禁：仅在 snapshot present、usage mode actual、fresh gate pass 且矩阵可写时输出。
- 更新 `/sprint-archive` 与 `/sprint-exps` 命令说明，加入 snapshot 缺失、过期、失败、覆盖不足或 fallback 时的 manual map 恢复分支。
- 增加聚焦测试，覆盖 manual map 合并、`post_command_target` 选择、缺少 session 的 `recommended_action`、刷新后矩阵门禁和脱敏边界。
- 明确 AI Usage 产物不得持久化原始 session、prompt、系统/开发者指令、本机绝对路径、密钥、`.env` 内容或完整工具输出。

## 能力影响

### 新增能力

无。

### 修改能力

- `governance-workflow-tooling`: 补强 AI Usage manual map 恢复流程、snapshot fresh gate 和真实 token 矩阵输出门禁。

## 影响范围

- 后端产品 API：无影响。
- 数据库：无影响。
- 前台 Web / 后台管理端：无影响。
- 对象存储和媒体链路：无影响。
- 治理脚本：影响 `scripts/extract-ai-usage.py`、`scripts/generate-sprint-fact-sheet.py` 的帮助、门禁或测试覆盖。
- Agent 技能：影响 `/sprint-archive`、`/sprint-exps` 相关说明。
- 文档与事实源：影响 `data/ai-usage/sprints/<sprint-id>.json` 派生产物与 OpenSpec 治理规格。
