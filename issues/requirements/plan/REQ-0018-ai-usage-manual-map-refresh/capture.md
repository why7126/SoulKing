---
req_id: REQ-0018-ai-usage-manual-map-refresh
status: captured
created_at: 2026-08-27 10:50:03
updated_at: 2026-08-27 10:50:03
recorded_at: 2026-08-27 10:50:03
recorded_by: codex
source: docs/knowledge-base/retrospectives/sprint-001-retrospective.md
priority_hint: P2
parent_requirement:
---

# 一句话
固化 AI Usage 手动映射与刷新流程，使本地 session 自动归因不足时能按标准步骤恢复真实统计快照。

# 原始描述
用户要求“固化 AI Usage 手动映射与刷新流程”。该需求来源于 `sprint-001` 经验复盘的后续行动项 T-003：`sprint-001` 初次归档时 AI Usage 处于 `estimated_fallback`，后续通过本地 session JSONL 与 `tmp/sprint-001-ai-usage-manual-map.json` 才恢复为 `actual`。

# 待澄清
- [ ] 手动映射流程应优先固化为脚本帮助、命令技能说明、长期文档，还是三者同步。
- [ ] manual map 的标准字段、样例路径和校验失败提示需要在 `/req-explore` 中确认。
- [ ] 缺少 session JSONL 时的 recommended_action 是否只提示人工补充，还是提供可复制的最小刷新命令。

# 探索结论
（/req-explore 后人工确认写入）
