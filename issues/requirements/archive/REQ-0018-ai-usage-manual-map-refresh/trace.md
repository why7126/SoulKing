---
requirement_id: REQ-0018-ai-usage-manual-map-refresh
status: done
priority: P2
created_at: 2026-08-27 10:50:03
updated_at: 2026-08-31 10:22:52
related_spec:
related_changes: []
openspec_changes:
  - change_id: update-ai-usage-manual-map-refresh
    type: update
    status: archived
knowledge_base_refs:
  - docs/knowledge-base/README.md
  - docs/knowledge-base/retrospectives/sprint-001-retrospective.md
cross_cutting_tags: []
lifecycle:
  captured: 2026-08-27 10:50:03
  generated: 2026-08-31 08:45:32
  completed: 2026-08-31 08:59:00
  reviewed: 2026-08-31 09:00:00
  approved: 2026-08-31 09:00:00
iteration: sprint-002
---

# Trace

## 当前状态
- 状态：done
- 阶段：archive
- 事实源：`issues/requirements/review/REQ-0018-ai-usage-manual-map-refresh/requirement.md`

## 关联文件
- `capture.md`
- `requirement.md`
- `user-stories.md`
- `business-flow.md`
- `acceptance.md`
- `review.md`

## 关联来源
- `docs/knowledge-base/retrospectives/sprint-001-retrospective.md` 后续行动项 T-003
- 来源 Sprint：`sprint-001`
- 来源命令：`/sprint-exps`

## 关联 OpenSpec
- `update-ai-usage-manual-map-refresh`（archived）

## Knowledge-base Cross-cutting Report

| 标签 | 引用文档 | 将写入 acceptance 的 AC 条数 |
|---|---|---:|
| 无横切 AC | `docs/knowledge-base/README.md` | 0 |
| AI Usage 复盘经验 | `docs/knowledge-base/retrospectives/sprint-001-retrospective.md` | 8 |

## 产品数据采集与链路观测
机器可校验声明记录在 `acceptance.md`。结论为不适用：本需求只影响仓库内 AI Agent 治理统计流程和 `data/ai-usage` 派生产物，不改变 SoulKing 产品侧 API、数据库、请求日志、行为事件、Task Trace、前台请求封装、后台请求封装、媒体链路或对象存储读写。

## 变更记录
- 2026-08-31 09:18:00：通过 `/req-opsx` 创建 OpenSpec Change `update-ai-usage-manual-map-refresh`，等待实现。
- 2026-08-31 09:00:00：需求评审通过，状态更新为 approved，准备纳入 Sprint。
- 2026-08-31 08:59:00：补齐 `user-stories.md`、`business-flow.md`、`acceptance.md`，记录知识库适用性与产品数据采集 N/A 声明，状态更新为 pending_review。
- 2026-08-31 08:45:32：生成 `requirement.md` PRD 草稿，状态更新为 draft。
- 2026-08-27 10:50:03：捕获需求，记录 AI Usage 手动映射与刷新流程固化诉求。
- 2026-08-31 10:18:42 workflow-sync：状态同步为 done（Change archived）
