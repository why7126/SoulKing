---
purpose: OpenSpec Change design
content: AI Usage manual map 与 Sprint snapshot 刷新流程设计
created_at: 2026-08-31 09:18:00
updated_at: 2026-08-31 09:18:00
---

# 设计

## 背景

当前 AI Usage 链路已经包含 `scripts/extract-ai-usage.py --manual-map`、Sprint snapshot、Fact Sheet fresh gate 与 token 矩阵渲染，但操作者缺少稳定说明：manual map 的键如何选择、字段如何合并、刷新后复查哪些指标、fallback 时下一步如何恢复。REQ-0018 来源于 `sprint-001` 复盘行动项 T-003，目标是把一次临时恢复经验固化为治理命令可消费的标准流程。

## 目标与非目标

**目标：**

- 让 manual map 输入格式、键选择和字段集合可被 CLI 帮助、技能说明和测试复用。
- 让 Sprint archive 与 Sprint exps 在 AI Usage snapshot 不可信时给出一致的 `recommended_action`。
- 确保真实 token 矩阵只基于刷新后的 `actual` snapshot 与通过的 fresh gate 输出。
- 通过聚焦测试保护 manual map 合并、矩阵门禁和脱敏边界。

**非目标：**

- 不新增 SoulKing 产品侧行为采集、请求日志、Task Trace 或 API。
- 不修改 `app/`、`app/static/`、数据库模型、MinIO 对象结构或 Docker 部署拓扑。
- 不把原始 session JSONL、prompt、系统/开发者指令或本机敏感路径复制进仓库。

## 设计决策

### D1. 将 manual map 作为本地输入，仓库只保存脱敏后的 snapshot

manual map 和 session JSONL 都是恢复输入，不是长期事实源。实现阶段只允许 `data/ai-usage/sprints/<sprint-id>.json` 保存脱敏后的 command usage facts、覆盖摘要、矩阵摘要和推荐动作；不得持久化原始 session 内容、完整工具输出、真实本机绝对路径、密钥、Cookie、Authorization header 或 `.env` 内容。

### D2. 同时支持 `turn_hash` 与 `source_session_hash`

`turn_hash` 用于对单次命令或单个 turn 做精确归因；`source_session_hash` 用于同一 session 中多个相关 turn 的批量补齐。合并时 manual map 字段只补足归因目标和 workflow 元数据，不覆写真实 token_count 事件本身。

### D3. Fact Sheet summary 是刷新后的复查入口

刷新 snapshot 后，操作者必须重新运行 Fact Sheet summary，并以刷新后的 `fresh_gate`、`snapshot_status`、`ai_usage_mode`、coverage、totals 和 `usage_matrices_summary` 判断是否可输出矩阵。不得沿用刷新前的 fallback 结论，也不得在 blocker/fallback 状态下生成真实 token 成本矩阵。

### D4. Sprint 命令说明只提供恢复分支，不自动猜测真实用量

`/sprint-archive` 与 `/sprint-exps` 在 snapshot missing/stale/failed/fallback/coverage blocker 时输出恢复分支和 `recommended_action`。它们不得手工估填 token 数字，也不得把 `estimated_fallback` 标记成 `actual`。

## 冲突处理

本需求无 `prototype/web/`、PNG 或 UI context；无 UI 冲突。优先级链路退化为 `acceptance.md > ui-design.md > openspec/specs`，本 Change 按 `acceptance.md` 的 AC-001 至 AC-008 生成治理规格。

## 产品数据采集与链路观测

product_data_collection_observability:
- status = not_applicable
- reason: 本 Change 只影响仓库内 AI Agent 治理统计流程、CLI 帮助、技能说明、Fact Sheet 门禁和 `data/ai-usage` 派生产物；不改变 SoulKing 产品侧 API、数据库、请求日志、行为事件、Task Trace、前台请求封装、后台请求封装、媒体链路或对象存储读写。
- affected_layers: []
- validation: `/req-opsx` 阶段已复核 REQ 声明并计划在实现前运行 `python scripts/validate-product-data-observability-gates.py --change update-ai-usage-manual-map-refresh`。

## 风险与取舍

- [Risk] manual map 字段说明过宽，可能被误用于写入敏感 session 内容。  
  Mitigation: 规格和测试明确只允许保存脱敏归因字段和聚合结果。
- [Risk] `estimated_fallback` warning 被误认为可关闭验收。  
  Mitigation: Fact Sheet 矩阵门禁要求 `actual`、present snapshot 和 fresh gate pass 同时成立。
- [Risk] Sprint archive/exps 说明与脚本行为漂移。  
  Mitigation: 实现任务同时修改技能说明和聚焦测试。

## 迁移计划

无数据库迁移、API 迁移或部署迁移。实现后通过 Workflow Sync、OpenSpec 校验、产品数据门禁和相关 pytest 验证治理链路。

## 未决问题

无。
