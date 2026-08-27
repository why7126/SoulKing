---
purpose: Sprint 生命周期
content: Sprint 规划、执行、验收、归档和知识库沉淀规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 01:30:00
---

# Sprint 生命周期

- 进行中 Sprint 放在 `iterations/change/sprint-*`。
- 完成 Sprint 归档到 `iterations/archive/sprint-*`。
- `/sprint-propose` 只能纳入已评审通过的 REQ/BUG 或已批准 Change。
- `/sprint-apply` 实现前必须输出 Knowledge Gate。
- `/sprint-exps` 将复盘、行动项和可复用经验写入 `docs/knowledge-base/`。

## Sprint 选择门禁

- `/sprint-propose` SHOULD 在选择或创建 Sprint 前运行 `python scripts/validate-sprint-selection.py [--sprint <sprint-id>]`。
- 未指定 Sprint 时，若没有 active Sprint，可默认创建最大规范编号加一的新 Sprint；若只有一个 active Sprint，默认使用该 Sprint；若存在两个或以上 active Sprint，必须阻断并要求用户显式指定。
- 用户显式指定尚不存在的 Sprint 时，该 Sprint ID 必须等于当前最大规范编号加一，不得跳号。
- 已存在两个 active Sprint 时，不得创建第三个 active Sprint。
- 若已有当前 Sprint 且追加范围导致容量超过 120%，必须引导用户拆分范围、移出低优先级项、替换范围，或指定下一个连续 Sprint 重新规划；下一个 Sprint 必须通过 `python scripts/validate-sprint-selection.py --sprint <sprint-id>`。
- 已存在 Sprint 追加或修正正式范围时，必须先更新 `sprint.yaml` 机器事实源，再由 Workflow Sync 刷新四件套和 trace；不得只手工编辑 `sprint.md` 或派生 marker block。
- `/sprint-propose` 写入或更新范围后，必须运行 `python scripts/validate-sprint-scope.py <sprint-id> [--item <REQ|BUG|change-id>]`，确认 `sprint.md` `## 1. 目标` 编号列表、`## 2. Scope` 六列主表和 workflow-sync 派生表均包含正式范围。
- `sprint.md` `## 2. Scope` 主表保持 `类型 | 编号 | 标题 | 状态 | 估算 | 说明` 六列；派生分组表可使用更适合机器同步的结构。

## Sprint 容量门禁

- `/sprint-propose` 在生成正式四件套、更新 Sprint scope 或更新 REQ/BUG/Change trace 前必须计算 `capacity_usage = estimated_person_days / capacity_person_days`。
- 新建 Sprint 默认容量基线来自 `project.yaml` 的 `ai.sprint_capacity.capacity_person_days`；若 `project.yaml` 未配置，必须在 Sprint 提议时显式确认容量，不得猜测。
- 若 `capacity_person_days` 或 `estimated_person_days` 缺失，必须先补齐容量或估算输入，不得默认通过。
- 当 `estimated_person_days <= capacity_person_days` 时，容量门禁为 `pass`，继续既有 Review Gate、Readiness Gate、Sprint Selection Gate 和 Scope Gate。
- 当 `capacity_person_days < estimated_person_days <= capacity_person_days * 1.2` 时，容量门禁为 `pass_with_risk`，允许继续，但 Sprint 文档必须记录容量风险、fix 缓冲影响和延后项建议。
- 当 `estimated_person_days > capacity_person_days * 1.2` 时，容量门禁为 `blocked`，不得生成正式四件套，不得写入当前 Sprint scope，不得更新 REQ/BUG/Change trace 的 Sprint 关联；必须拆分 Sprint、移出低优先级项或替换范围后重新评估。
- `sprint.yaml` 创建、追加或修正正式范围后必须记录 `capacity_person_days`、`estimated_person_days`、`capacity_usage`、`fix_buffer_person_days`、`fix_buffer_ratio` 和 `capacity_gate`；`capacity_gate` 至少包含 `capacity_person_days`、`estimated_person_days`、`capacity_usage`、`result` 和 `note`。
- fix 缓冲建议保留 30% 以上；低于建议线但未超过 120% 时不自动阻断，但必须在 Sprint 文档中提示后续新增范围优先拆分或移出低优先级项。

## Sprint 归档 stale scan

- `/sprint-archive` 关闭 Sprint 前必须通过 archive readiness 内置的 Sprint close stale scan。
- stale scan 阻断四件套和 scoped REQ/BUG 子文档中与真实生命周期冲突的中间态文案，包括“待 `/req-opsx`”、“待 `/bug-opsx`”、“待 `/opsx-apply`”、待开发、待实现、待验收、archived Change 的 `proposed` / `applied` 语义、archived Change 的 active 路径引用，以及旧归档路径 `openspec/changes/archive/` canonical 引用。
- 单独排查 stale 文案时运行 `python scripts/check-sprint-close-stale-scan.py --sprint <sprint-id>`；命中 workflow-sync marker 派生块时应重新同步，人工说明区才可聚焦改写。
- 10 个及以上 Change 的 Sprint 归档或复核应优先读取 readiness / Fact Sheet 的 `change_batches` 摘要，再按 blocker、warning 或 evidence hint 展开必要原始 Change 文档。

## 产品数据采集与链路观测门禁

Sprint 纳入、执行或归档的范围若涉及 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测，必须读取或确认引用 `docs/standards/product-data-collection-observability.md`，并复核相关 REQ、BUG 或 Change 是否记录 `product_data_collection_observability` 适用层级、N/A 原因和验证摘要。

Sprint 文档只保留门禁状态摘要，不复制完整采集规范正文。关闭 Sprint 前可运行 `python scripts/validate-product-data-observability-gates.py --sprint <sprint-id>` 做聚焦校验。
