---
requirement_id: REQ-0018-ai-usage-manual-map-refresh
created_at: 2026-08-31 08:59:00
updated_at: 2026-08-31 08:59:00
source: requirement.md
---

# 用户故事

- US-001：作为项目维护者，我希望 manual map 的键、字段和适用场景有清晰说明，以便在自动归因不足时快速补齐 AI Usage 归因。
- US-002：作为执行 Sprint 归档或复盘的 AI Agent，我希望在 snapshot 缺失、过期、失败或 fallback 时得到可复制的恢复命令链，以便先刷新事实源再输出真实 token 矩阵。
- US-003：作为治理审阅者，我希望 Fact Sheet 能明确阻止不满足 fresh gate 的真实成本矩阵输出，以便避免把 `estimated_fallback` 误读为真实 token 统计。
- US-004：作为项目维护者，我希望 AI Usage 产物保持脱敏边界，以便本地 session、prompt、系统/开发者指令、本机路径和密钥不会进入仓库事实源。

## 验收要点
- manual map 的标准字段、键选择和最小样例可被后续实现文档或 CLI 帮助消费。
- 从 fallback 恢复到 actual 的命令链包含刷新、复查和矩阵再生成步骤。
- 缺少 session JSONL 或 token_count 事件时，命令输出保留明确 recommended_action，且不写真实 token 矩阵。
- 安全边界覆盖 AI Usage 输入、输出、命令摘要和长期文档。
