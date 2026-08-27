---
note: workflow-sync — workflow-sync 自动同步 — 1/1 Change archived；0 applied；Sprint `planning`
created_at: 2026-08-27 08:54:38
updated_at: 2026-08-27 09:23:50
---

# sprint-002 Sprint 容量治理加固

## 1. 目标

应用 ProjectTilesFST 的 Sprint 容量配置和超出策略学习项，补齐 SoulKing 的容量门禁规则、技能、OpenSpec 规格、脚本刷新和聚焦测试。

Sprint 目标编号列表：

- `tighten-soulking-sprint-capacity-governance`

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| Change | tighten-soulking-sprint-capacity-governance | tighten soulking sprint capacity governance | archived | 2 人天 | archived `tighten-soulking-sprint-capacity-governance`（2026-08-27 09:23:32） |

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `tighten-soulking-sprint-capacity-governance` | — | archived | archived `tighten-soulking-sprint-capacity-governance`（2026-08-27 09:23:32） |
<!-- workflow-sync:scope-changes:end -->

REQ：无 已纳入正式范围；BUG：无 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 0 个范围项关联 Change，另有 1 个纯 Change；1 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

| 项 | 值 |
|---|---:|
| 容量基线 | 30 人天 |
| 估算 | 3 SP / 2 人天 |
| 容量占用 | 6.67% |
| fix 缓冲 | 28 人天 / 93.33% |

容量门禁通过。本 Sprint 从 `sprint-001` 的超载状态中拆出，只承载当前治理学习应用；项目默认 Sprint 容量基线已调整为 30 人天。

## 4. 里程碑

- 建立 OpenSpec Change 与 Sprint scope。
- 更新规则、技能、脚本和 OpenSpec delta spec。
- 补充聚焦测试。
- 生成 `/spec-study` 学习报告。
- 运行治理校验、Workflow Sync 和 AI Usage hook。

## 5. 风险

- 后续若团队规模变化，应先调整 `project.yaml` 的项目默认容量基线，再由新 Sprint 继承；历史 Sprint 不反向改写。
- 不得修改 `app/`、`app/static/` 或 `packaging/` 业务运行时代码。

## 6. 知识库承接

- 来自 `/spec-study ProjectTilesFST sprint 容量配置和超出策略` 的学习结论。

## 7. 横切预防清单

- 维护事实唯一归属：详细容量规则进入 Sprint lifecycle、sprint-propose skill 和 OpenSpec delta spec。
- 新增脚本逻辑必须有聚焦测试。
- 不写入学习对象源码或未脱敏本机路径到长期文档。

## 8. 依赖

```text
ProjectTilesFST 只读学习
└── tighten-soulking-sprint-capacity-governance
    ├── rules/iterations-lifecycle.md
    ├── .agents/skills/sprint-propose/SKILL.md
    ├── scripts/add-sprint-scope-item.py
    └── tests/test_sprint_propose_capacity_gate.py
```

## 9. 发布计划

本 Sprint 不产生产品版本发布。

## 10. 关联文档

- `openspec/archive/2026-08-27-tighten-soulking-sprint-capacity-governance/`
- `docs/spec-logs/`
