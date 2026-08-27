---
purpose: Sprint 经验复盘
content: sprint-001 治理学习加固的流程、质量、Token 使用和后续行动项
created_at: 2026-08-27 10:46:00
updated_at: 2026-08-27 10:46:00
---

# sprint-001 经验复盘

## 概况

`sprint-001` 是治理学习加固 Sprint，范围为 8 个 OpenSpec Change，不包含正式 REQ 或 BUG。Sprint 已归档至 `iterations/archive/sprint-001/`，8 个 Change 均已归档，任务完成度为 59/59，归档路径残留检查为 0，Fact Sheet warning 为 0。

本 Sprint 的主要价值是把跨项目治理经验沉淀到 ProjectSoulKing：Agent 上下文预算、目录结构边界、Sprint/Issue/OpenSpec 流程质量、数据采集与链路观测门禁，以及归档与 AI Usage 统计能力。它不产生用户可见产品版本发布，也不影响 API、数据库、前台 Web、后台管理端或部署拓扑。

## 流程复盘

| 维度 | 观察 | 经验 |
|------|------|------|
| Sprint 范围 | 8 个 Change、59 个任务全部完成，容量登记为 3 人天，实际范围偏治理密集。 | 治理 Sprint 应显式区分“学习型 Change”和“应用型 Change”，避免学习材料、脚本修正和归档工作混在同一估算口径里。 |
| 归档质量 | 归档 readiness、产品数据采集门禁、Issue promote 预检和 stale scan 均通过。 | 关闭 Sprint 前集中跑门禁是有效的，但 Sprint 四件套中派生区与人工说明区仍需要 stale scan 护栏。 |
| 证据读取 | Fact Sheet summary 足以覆盖 scope、tasks、warnings、AI usage 和 token risks。 | `/sprint-exps` 应优先读取 Fact Sheet summary，只有 warning、needs_detail 或用户指定 focus 时再回读原文。 |
| 知识沉淀 | 本次核心产物是治理能力，不是业务功能。 | 复盘应沉淀为后续命令可读的行动项，而不是复制 Change trace。 |

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据/说明 |
|------|----|-----------|
| 精确 token 统计 | 有 | 来源：`data/ai-usage/sprints/sprint-001.json` |
| AI usage mode | actual | Fact Sheet: `ai_usage_snapshot.ai_usage_mode` |
| Snapshot status | present | Fact Sheet: `ai_usage_snapshot.snapshot_status` |
| Fresh gate | pass | Fact Sheet: `ai_usage_snapshot.fresh_gate.status` |
| Matrix write gate | pass | 必须 fresh gate pass、actual/present 且矩阵存在才可输出真实矩阵 |
| Freshness baseline | 2026-08-27T01:26:01Z | 来源：`acceptance-report.md:updated_at` |
| Generated at | 2026-08-27T02:39:46.987991Z | `data/ai-usage/sprints/sprint-001.json` |
| command_run_count | 46 | snapshot totals |
| model_call_count | 460 | snapshot totals |
| tool_call_count | 801 | snapshot totals |
| input_tokens | 70,346,238 | snapshot totals |
| cached_input_tokens | 67,623,168 | snapshot totals |
| output_tokens | 264,572 | snapshot totals |
| reasoning_output_tokens | 24,422 | snapshot totals |
| total_tokens | 70,679,165 | snapshot totals |
| retry_count | 0 | snapshot totals |
| 矩阵规模 | 2 行 x 22 列 | `usage_matrices.rows` / `usage_matrices.columns` |

矩阵口径：`Total` 与 Sprint 行按唯一 command run 汇总；REQ/BUG 行是对象归因视图，同一 command run 关联多个 REQ/BUG 时可在多个对象行出现，因此对象行不应直接相加后与 `Total` 比较。`-` 表示该 workflow 阶段在当前 snapshot 中未采集或未归因，不等价于真实 `0`；只有已观测 workflow 列中的数字 `0` 才表示真实零消耗。矩阵数据来自 `data/ai-usage/sprints/<sprint-id>.json` 经 Fact Sheet 渲染输出。

### total_tokens 矩阵

| 对象 | Capture | BUG-Capture | REQ-Capture | BUG-Explore | REQ-Explore | REQ-Generate | BUG-Generate | REQ-Complete | BUG-Complete | REQ-Review | BUG-Review | REQ-Opsx | BUG-Opsx | Opsx-Explore | Opsx-Propose | Opsx-Apply | Opsx-Modify | Opsx-Archive | Sprint-Propose | Sprint-Explore | Sprint-Apply | Sprint-Archive |
| ------ | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: |
| Total | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 30683 | 56369545 | - | 13821475 | - | - | - | 20220 |
| sprint-001 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 30683 | 56369545 | - | 13821475 | - | - | - | 20220 |

### input_tokens 矩阵

| 对象 | Capture | BUG-Capture | REQ-Capture | BUG-Explore | REQ-Explore | REQ-Generate | BUG-Generate | REQ-Complete | BUG-Complete | REQ-Review | BUG-Review | REQ-Opsx | BUG-Opsx | Opsx-Explore | Opsx-Propose | Opsx-Apply | Opsx-Modify | Opsx-Archive | Sprint-Propose | Sprint-Explore | Sprint-Apply | Sprint-Archive |
| ------ | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: |
| Total | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 30505 | 56083487 | - | 13775568 | - | - | - | 20036 |
| sprint-001 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 30505 | 56083487 | - | 13775568 | - | - | - | 20036 |

### output_tokens 矩阵

| 对象 | Capture | BUG-Capture | REQ-Capture | BUG-Explore | REQ-Explore | REQ-Generate | BUG-Generate | REQ-Complete | BUG-Complete | REQ-Review | BUG-Review | REQ-Opsx | BUG-Opsx | Opsx-Explore | Opsx-Propose | Opsx-Apply | Opsx-Modify | Opsx-Archive | Sprint-Propose | Sprint-Explore | Sprint-Apply | Sprint-Archive |
| ------ | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: |
| Total | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 178 | 240017 | - | 23593 | - | - | - | 184 |
| sprint-001 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 178 | 240017 | - | 23593 | - | - | - | 184 |

### model_call_count 矩阵

| 对象 | Capture | BUG-Capture | REQ-Capture | BUG-Explore | REQ-Explore | REQ-Generate | BUG-Generate | REQ-Complete | BUG-Complete | REQ-Review | BUG-Review | REQ-Opsx | BUG-Opsx | Opsx-Explore | Opsx-Propose | Opsx-Apply | Opsx-Modify | Opsx-Archive | Sprint-Propose | Sprint-Explore | Sprint-Apply | Sprint-Archive |
| ------ | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: | ------: |
| Total | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 | 356 | - | 96 | - | - | - | 1 |
| sprint-001 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 | 356 | - | 96 | - | - | - | 1 |

### 高消耗来源

| 来源 | 影响 | 证据 | 优化方案 |
|------|------|------|----------|
| OpenSpec Change 执行链路 | high | Fact Sheet: 8 个 Change，59/59 tasks；Opsx-Apply 约 5,636.95 万 total tokens、356 次模型调用。 | 每个 Change 执行前先读 `tasks.md` 摘要与相关规则摘要；跨项目学习类 Change 分批处理，避免一次性展开大量归档材料。 |
| OpenSpec 归档链路 | high | Opsx-Archive 约 1,382.15 万 total tokens、96 次模型调用。 | 归档前使用 readiness/fact-sheet/stat 命令聚合证据，只在 blocker 或 warning 处回读原文片段。 |
| 归档路径与历史资产查找 | medium | Fact Sheet token risk: Archive lookup，建议从 `sprint.yaml` change ids 解析 archive paths。 | 禁止宽泛搜索 `openspec/archive/**` 和 legacy `openspec/changes/archive/**`；优先用脚本解析 canonical archive path。 |
| Sprint 四件套与派生区 | medium | Fact Sheet: 四件套均小于 200 行，但包含 workflow-sync 派生内容和人工关闭记录。 | 复盘默认读取 summary；若需要修订回链，仅分段读取目标文件，不复制派生表全文。 |
| 规则与 Skill 重复读取 | medium | 本 Sprint 主要是治理规则、Skill 与脚本迭代，容易重复读取 `rules/`、`.agents/skills/`。 | 同会话复用已读摘要；文件版本未变化时只补读相关片段。 |
| 命令输出与日志 | low | retry_count 为 0；warning_count 为 0；无失败重跑放大。 | 长日志使用 `max_output_tokens`、`--summary`、`--json` compact 输出；测试失败先保留摘要与首个错误。 |

### 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|----|--------|------|------------|------|
| T-001 | P1 | 为下一轮治理 Sprint 明确学习型 Change 与应用型 Change 的容量分组，避免治理学习范围膨胀。 | `/sprint-propose` | open |
| T-002 | P1 | 将 Fact Sheet summary 作为 `/sprint-exps` 默认输入边界，只有 warning、needs_detail 或用户指定 focus 时回读原文。 | `/spec-opt` | open |
| T-003 | P2 | 为 AI Usage 手动 session 映射保留 tmp 手工映射流程说明，减少归档后 estimated_fallback 返工。 | `/req-capture` | open |
| T-004 | P2 | 对跨项目学习类 Change 增加搜索排除清单和 archive path 解析脚本优先级。 | `/spec-opt` | open |
| T-005 | P3 | 对 Sprint 四件套关闭记录增加 AI Usage 刷新后的回链校验，避免 acceptance 文案与真实 snapshot 脱节。 | `/bug-capture` | open |

## 需求与设计复盘

本 Sprint 没有正式 REQ 或 BUG，范围全部来自治理 Change。优点是可以快速加固 PM Harness 与 OpenSpec 流程；代价是业务价值不如需求型 Sprint 直观，容量与验收口径更依赖 Change 文档、脚本校验和知识库沉淀。

后续治理类 Sprint 建议在规划阶段补充三类验收表达：治理资产变更清单、脚本或门禁的可复验命令、下一命令如何消费这些治理结果。这样能降低归档时“文档已改但流程是否吃到”的确认成本。

## 开发质量复盘

本 Sprint 的质量信号偏好：脚本化校验优先于人工检查，路径残留和 stale 文案都通过自动门禁收束。`product_data_collection_observability` 也被纳入 Sprint 关闭摘要，说明治理 Change 已经能覆盖跨层门禁声明。

需要修正的是 AI Usage 统计链路：初次归档时缺少本地 session JSONL，导致关闭记录曾以 `estimated_fallback` 表述。后续通过 `tmp/sprint-001-ai-usage-manual-map.json` 补齐手动映射后，snapshot 已恢复为 `actual`。这类返工应沉淀为命令前置检查，而不是等复盘阶段再修。

## 可复用抽象

| 抽象 | 适用场景 | 建议 |
|------|----------|------|
| Sprint Fact Sheet | Sprint 归档、复盘、验收摘要、AI Usage 写入 | 继续作为 `/sprint-exps` 的主输入，扩展字段时保持 compact summary 优先。 |
| Archive residual checker | Sprint 归档后路径一致性 | 保留为归档与复盘共用门禁，避免旧 active path 被写入长期文档。 |
| AI Usage manual map | 本地 session 自动归因不足时 | 将手动 map 的格式、校验和重跑命令固化到操作说明或脚本帮助中。 |
| Workflow Sync stale scan | 四件套派生区与人工说明区一致性 | 继续用于关闭前检查，并增加复盘回链类文案的覆盖。 |

## 后续 Capture 建议

以下事项未自动创建 Issue，仅作为后续 capture 文案：

### Follow-up 1

- 建议命令：`/req-capture`
- 类型倾向：REQ
- 标题：固化 AI Usage 手动映射与刷新流程
- 背景：`sprint-001` 初次归档时 AI Usage 为 `estimated_fallback`，后续通过本地 session JSONL 与 `tmp/sprint-001-ai-usage-manual-map.json` 才恢复为 `actual`。
- 影响范围：`scripts/extract-ai-usage.py`、`scripts/generate-sprint-fact-sheet.py`、Sprint archive/exps 命令说明。
- 建议验收要点：给定 session JSONL 与 manual map 后，snapshot fresh gate 为 pass，复盘可生成四张 token 矩阵；缺少 session 时输出明确 recommended_action。
- 来源 Change/Sprint/命令：`sprint-001` / `/sprint-exps`

### Follow-up 2

- 建议命令：`/bug-capture`
- 类型倾向：BUG
- 标题：Sprint 关闭记录在 AI Usage 刷新后可能保留过期 fallback 文案
- 背景：`sprint-001` 的关闭记录曾写入 `estimated_fallback`，后续 snapshot 已更新为 `actual`，需要避免长期文档与事实源脱节。
- 影响范围：`iterations/archive/<sprint>/sprint.md`、`acceptance-report.md`、Fact Sheet stale/fresh gate。
- 建议复现要点：先以 fallback 关闭 Sprint，再补齐 session JSONL 刷新 snapshot，检查关闭记录是否同步提示或自动修订。
- 来源 Change/Sprint/命令：`sprint-001` / `/sprint-exps`

## 结论

`sprint-001` 达成治理加固目标，归档与复盘输入质量良好。最大经验不是某个单点规则，而是命令链路需要把“读取边界、门禁脚本、AI Usage 事实源、长期文档回链”组合成闭环。下一轮治理 Sprint 应优先降低 Opsx-Apply 与 Opsx-Archive 的上下文成本，并把 AI Usage 刷新前置化。
