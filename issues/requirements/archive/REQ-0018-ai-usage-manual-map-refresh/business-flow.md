---
requirement_id: REQ-0018-ai-usage-manual-map-refresh
created_at: 2026-08-31 08:59:00
updated_at: 2026-08-31 08:59:00
source: requirement.md
---

# 业务流程

```text
Sprint archive / Sprint exps / 治理复盘
  -> 读取 Fact Sheet summary
  -> 检查 AI Usage snapshot
       |-- fresh_gate=pass + actual + matrices
       |     -> 允许生成真实 token 使用矩阵
       |
       |-- missing / stale / failed / fallback / coverage blocker
             -> 输出 blocker 与 recommended_action
             -> 操作者提供 local session JSONL
             -> 操作者提供 manual map
             -> extract-ai-usage 刷新 sprint snapshot
             -> 重新读取 Fact Sheet summary
             -> 通过后再生成 token 使用矩阵
```

## Manual Map 恢复链路

```text
local session JSONL
  + manual map
      - turn_hash 或 source_session_hash
      - requirements / bugs / changes
      - sprint_id / workflow_event
      - post_command_target / attribution_confidence
  -> scripts/extract-ai-usage.py --session-jsonl ... --manual-map ... --sprint ...
  -> data/ai-usage/sprints/<sprint-id>.json
  -> scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary
  -> scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --ai-usage-markdown
```

## 与父需求差异
- 本需求无父需求。
- 本需求来源于 `sprint-001` 复盘行动项 T-003，是对治理流程的独立固化，不改变 SoulKing 产品功能。

## 关键边界
- 原始 session JSONL 保持本地输入，不复制进仓库。
- AI Usage 产物只保存脱敏后的 command usage facts。
- 缺少真实 token 事件或 fresh gate 未通过时，不能生成真实 token 成本矩阵。
- 后续若改变工作流语义或命令契约，必须通过 OpenSpec Change 承载。
