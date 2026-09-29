---
requirement_id: REQ-0018-ai-usage-manual-map-refresh
title: 固化 AI Usage 手动映射与刷新流程
terminal: multi
version: v1
status: done
owner: product
source: capture.md
priority: P2
created_at: 2026-08-31 08:45:32
updated_at: 2026-08-31 10:18:42
parent_requirement:
related_spec:
---

# 固化 AI Usage 手动映射与刷新流程

## 背景
`sprint-001` 初次归档时，AI Usage 因缺少可用本地 session JSONL 或自动归因不足，曾以 `estimated_fallback` 形态进入关闭链路。后续通过本地 session JSONL 与 `tmp/sprint-001-ai-usage-manual-map.json` 手动补齐映射后，Sprint snapshot 才恢复为 `actual`。

这说明当前能力已经具备部分技术入口，例如 `scripts/extract-ai-usage.py --manual-map`、Sprint snapshot、Fact Sheet fresh gate 与 token 矩阵渲染；但操作者缺少一套可复验、可复制、可审计的恢复流程。该需求用于把一次临时经验固化为后续 Sprint archive、Sprint exps 与治理复盘可以消费的标准流程。

## 目标用户
- 项目维护者
- 执行 `/sprint-archive`、`/sprint-exps`、`/opsx-*`、`/req-*`、`/bug-*` 的 AI Agent
- 需要复核 AI Usage 真实 token 统计的治理审阅者

## 用户价值
- 减少 Sprint 关闭或复盘阶段因 `estimated_fallback` 返工造成的人工排查成本。
- 让 manual map 的字段、输入、输出和复查命令有稳定说明，避免依赖临时对话记忆。
- 确保 token 使用矩阵只在 `fresh_gate=pass`、`snapshot_status=present`、`ai_usage_mode=actual` 且矩阵可用时生成。
- 在缺少 session 或 token_count 事件时给出明确 recommended_action，避免把 fallback 误当真实统计。

## 范围 In
- 定义 AI Usage manual map 的标准输入格式和字段语义。
- 固化从 `estimated_fallback` 恢复到 `actual` 的最小命令链路：提供 session JSONL、提供 manual map、刷新 sprint snapshot、复查 Fact Sheet fresh gate、重新生成 token 矩阵。
- 补强 `scripts/extract-ai-usage.py` 的帮助信息或相邻说明，使 `--manual-map` 的适用场景、键选择和字段集合可被操作者理解。
- 更新 Sprint archive / Sprint exps 相关命令说明，使 snapshot 缺失、过期、失败、覆盖不足或 fallback 时能给出 manual map 恢复分支。
- 增加聚焦测试，覆盖 manual map 合并、`post_command_target` 选择、缺少 session 的 recommended_action、刷新后矩阵门禁。
- 明确 AI Usage 产物不得持久化原始 session JSONL、prompt、系统/开发者指令、本机绝对路径、密钥、`.env` 内容或完整工具输出。

## 范围 Out
- 不新增 SoulKing 产品侧用户行为采集、请求日志、任务链路或流程节点。
- 不改变前台 Web、后台管理端或产品 API 行为。
- 不新增数据库表、业务接口、对象存储结构或媒体处理流程。
- 不手工估填 token 数字，不允许把 `estimated_fallback` 伪装为真实统计。
- 不要求 UI prototype 或用户可见页面。

## 功能要求
- FR-001：manual map 应支持以 `turn_hash` 或 `source_session_hash` 作为映射键，并说明两种键的适用场景。
- FR-002：manual map 应支持声明 `requirements`、`bugs`、`changes`、`sprint_id`、`workflow_event`、`release_sprints`、`release_version`、`post_command_target` 和 `attribution_confidence`。
- FR-003：刷新命令应支持同时传入 `--session-jsonl`、`--manual-map` 与 `--sprint`，生成或更新 `data/ai-usage/sprints/<sprint-id>.json`。
- FR-004：刷新后必须通过 Fact Sheet summary 复查 `fresh_gate`、`snapshot_status`、`ai_usage_mode`、coverage、totals 与 `usage_matrices_summary`，不得沿用刷新前结论。
- FR-005：只有当 snapshot 为 present、usage mode 为 actual、fresh gate 通过且矩阵可写时，才允许通过 `--ai-usage-markdown` 输出真实 token 矩阵。
- FR-006：当 session JSONL 缺失、路径不可用、缺少 token_count 事件、覆盖不足或矩阵缺失时，应输出明确 `recommended_action`，并阻止默认写入真实 token 成本矩阵。
- FR-007：Sprint archive 与 Sprint exps 命令说明应包含 manual map 恢复路径，减少归档后再返工刷新。
- FR-008：AI Usage 产物和命令摘要必须保持脱敏，不得写入原始 session、prompt、系统/开发者指令、本机绝对路径、密钥、Cookie、Authorization header、`.env` 内容或完整工具输出。

## UI 约束
- 本需求不涉及前台 Web、后台管理端或桌面界面。
- 若后续仅补充 CLI 帮助或命令说明，输出应保持简洁、可复制，并避免展示真实本机路径或敏感内容。

## 关联需求
- 来源复盘：`docs/knowledge-base/retrospectives/sprint-001-retrospective.md`
- 来源行动项：T-003
- 相关治理能力：`openspec/specs/governance-workflow-tooling/spec.md`

## 产品数据采集与链路观测
本需求的机器可校验声明记录在 `acceptance.md`。结论为不适用：本需求只影响仓库内 AI Agent 治理统计流程和 `data/ai-usage` 派生产物，不改变 SoulKing 产品侧 API、数据库、请求日志、行为事件、Task Trace、前台请求封装、后台请求封装、媒体链路或对象存储读写。

## 状态
- 当前状态：`approved`
- 当前阶段：需求评审通过，等待纳入 Sprint。
