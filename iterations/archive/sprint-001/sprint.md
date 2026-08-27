---
note: workflow-sync — workflow-sync 自动同步 — 8/8 Change archived；0 applied；Sprint `completed`
created_at: 2026-08-07 13:04:31
updated_at: 2026-08-27 10:46:00
---

# sprint-001 治理学习加固

## 1. 目标

将 ProjectTilesFST 中适合 ProjectSoulKing 的 Agent 上下文预算、目录结构、deploy / Mintlify / release 治理经验项目化应用到本项目。

Sprint 目标编号列表：

- `study-projecttilesfst-governance-hardening`
- `study-projectmoonbox-governance-hardening`
- `apply-projecttilesfst-spec-study-enhancements`
- `study-deepseek-harness-governance-hardening`
- `simplify-review-default-approval`
- `apply-tilesfst-governance-upgrade-learnings`
- `apply-tilesfst-workflow-quality-learnings`
- `apply-tilesfst-data-collection-governance-learnings`

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| Change | study-projecttilesfst-governance-hardening | study projecttilesfst governance hardening | archived | — | archived `study-projecttilesfst-governance-hardening`（2026-08-07 23:59:59） |
| Change | study-projectmoonbox-governance-hardening | study projectmoonbox governance hardening | archived | 1 人天 | archived `study-projectmoonbox-governance-hardening`（2026-08-21 10:04:47） |
| Change | apply-projecttilesfst-spec-study-enhancements | apply projecttilesfst spec study enhancements | archived | 1 人天 | archived `apply-projecttilesfst-spec-study-enhancements`（2026-08-21 09:16:52） |
| Change | study-deepseek-harness-governance-hardening | study deepseek harness governance hardening | archived | 1 人天 | archived `study-deepseek-harness-governance-hardening`（2026-08-21 09:17:17） |
| Change | simplify-review-default-approval | simplify review default approval | archived | 0.5 人天 | archived `simplify-review-default-approval`（2026-08-21 13:58:39） |
| Change | apply-tilesfst-governance-upgrade-learnings | apply tilesfst governance upgrade learnings | archived | 2 人天 | archived `apply-tilesfst-governance-upgrade-learnings`（2026-08-21 23:11:32） |
| Change | apply-tilesfst-workflow-quality-learnings | apply tilesfst workflow quality learnings | archived | 2 人天 | archived `apply-tilesfst-workflow-quality-learnings`（2026-08-27 01:20:00） |
| Change | apply-tilesfst-data-collection-governance-learnings | apply tilesfst data collection governance learnings | archived | 2 人天 | archived `apply-tilesfst-data-collection-governance-learnings`（2026-08-27 00:55:00） |

REQ：无 已纳入正式范围；BUG：无 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 0 个范围项关联 Change，另有 1 个纯 Change；0 archived，0 applied，1 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `study-projecttilesfst-governance-hardening` | — | archived | archived `study-projecttilesfst-governance-hardening`（2026-08-07 23:59:59） |
| `study-projectmoonbox-governance-hardening` | — | archived | archived `study-projectmoonbox-governance-hardening`（2026-08-21 10:04:47） |
| `apply-projecttilesfst-spec-study-enhancements` | — | archived | archived `apply-projecttilesfst-spec-study-enhancements`（2026-08-21 09:16:52） |
| `study-deepseek-harness-governance-hardening` | — | archived | archived `study-deepseek-harness-governance-hardening`（2026-08-21 09:17:17） |
| `simplify-review-default-approval` | — | archived | archived `simplify-review-default-approval`（2026-08-21 13:58:39） |
| `apply-tilesfst-governance-upgrade-learnings` | — | archived | archived `apply-tilesfst-governance-upgrade-learnings`（2026-08-21 23:11:32） |
| `apply-tilesfst-workflow-quality-learnings` | — | archived | archived `apply-tilesfst-workflow-quality-learnings`（2026-08-27 01:20:00） |
| `apply-tilesfst-data-collection-governance-learnings` | — | archived | archived `apply-tilesfst-data-collection-governance-learnings`（2026-08-27 00:55:00） |
<!-- workflow-sync:scope-changes:end -->

## 3. 工作量

- 容量：3 人天。
- 估算：1 人天。
- 容量使用率：33%。
- fix 缓冲：不涉及业务缺陷修复。

## 4. 里程碑

- 完成 OpenSpec Change 文档。
- 更新规则、脚本和学习报告。
- 运行治理校验。

## 5. 风险

- 规则加强后可能暴露现有目录或发布材料边界问题。
- 不得引入 ProjectTilesFST 的业务专属语境。

## 6. 知识库承接

- 本次为治理学习加固，无既有 Sprint 复盘依赖。
- Sprint 复盘已沉淀至 `docs/knowledge-base/retrospectives/sprint-001-retrospective.md`。

## 7. 横切预防清单

- 不修改 `app/`、`app/static/`、`packaging/`。
- 不修改 ProjectTilesFST。
- 不写入真实 env、密钥、运行时数据。
- Mintlify 仅作为公开站点投影，不替代 release 快照事实源。

## 8. 依赖

```text
ProjectTilesFST 只读学习
└── study-projecttilesfst-governance-hardening
    ├── agent-context-budget
    ├── directory-structure
    └── deploy-mintlify-release
```

## 9. 发布计划

本 Sprint 不产生产品版本发布。

## 10. 关联文档

- `openspec/archive/2026-08-07-study-projecttilesfst-governance-hardening/`
- `docs/spec-logs/`

## 11. 关闭记录

- 关闭时间：2026-08-27 09:24:19。
- 归档结果：8 个 Change 已归档，0 个阻塞，0 个需要继续归档。
- 产品数据采集与链路观测：适用。范围包含数据采集治理标准、流程门禁、校验脚本和验收声明；已运行 Sprint 级门禁复核。
- AI Usage：已通过本地 session JSONL 与 `tmp/sprint-001-ai-usage-manual-map.json` 刷新为 `actual`；fresh gate 与 matrix write gate 均通过，真实 token 矩阵见 `docs/knowledge-base/retrospectives/sprint-001-retrospective.md`。
