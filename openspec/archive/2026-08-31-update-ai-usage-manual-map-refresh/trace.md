---
change_id: update-ai-usage-manual-map-refresh
status: applied
created_at: 2026-08-31 09:18:00
updated_at: 2026-08-31 09:18:00
source: req-opsx
source_requirement: REQ-0018-ai-usage-manual-map-refresh
source_sprint: sprint-002
change_type: update
---

# update-ai-usage-manual-map-refresh Trace

```yaml
change_id: update-ai-usage-manual-map-refresh
status: applied
change_type: update
source_requirement: REQ-0018-ai-usage-manual-map-refresh
source_sprint: sprint-002
related_spec: governance-workflow-tooling
impact:
  backend: false
  web: false
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
  governance_scripts: true
  agent_skills: true
capabilities:
  new: []
  modified:
    - governance-workflow-tooling
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本 Change 只影响仓库内 AI Agent 治理统计流程、CLI 帮助、技能说明、Fact Sheet 门禁和 data/ai-usage 派生产物；不改变 SoulKing 产品侧 API、数据库、请求日志、行为事件、Task Trace、前台请求封装、后台请求封装、媒体链路或对象存储读写。
  validation: req-opsx 阶段已复核 REQ 声明；实现前运行 validate-product-data-observability-gates.py --change update-ai-usage-manual-map-refresh。
```

## Requirement Readiness Report

- 结论：ready。
- 需求六件套：`requirement.md`、`user-stories.md`、`business-flow.md`、`acceptance.md`、`trace.md`、`review.md` 已存在。
- 准入状态：`in_sprint`，已通过 `/req-review` 并纳入 `sprint-002`。
- OpenSpec 分类：`update`。

## Impact Analysis

```yaml
impact:
  backend: false
  web: false
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
  governance_scripts: true
  agent_skills: true
capabilities:
  new: []
  modified:
    - governance-workflow-tooling
```

## Conflict Report

- `prototype/web/`：不存在。
- UI Explore Gate：不适用。
- 冲突处理：按 `acceptance.md` 的 AC-001 至 AC-008 转为治理规格，不修改 UI 设计源。

## Validation Plan

- `openspec validate update-ai-usage-manual-map-refresh --strict`
- `python scripts/validate-product-data-observability-gates.py --change update-ai-usage-manual-map-refresh`
- `python scripts/sync-workflow-status.py --event req.opsx --req REQ-0018-ai-usage-manual-map-refresh --change update-ai-usage-manual-map-refresh --sprint auto`
- `python scripts/sync-workflow-status.py --event opsx.apply --change update-ai-usage-manual-map-refresh --sprint auto --dry-run`

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-08-31 09:18:00 | /req-opsx | 从 `REQ-0018-ai-usage-manual-map-refresh` 创建 OpenSpec Change。 |
