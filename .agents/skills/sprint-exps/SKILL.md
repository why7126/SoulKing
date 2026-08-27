---
name: "sprint-exps"
description: "Sprint 经验复盘 - 总结整迭代流程、需求、开发与质量经验，沉淀到 docs/knowledge-base"
created_at: 2026-08-06 00:00:00
updated_at: 2026-08-26 20:58:03
---

# sprint-exps

Use this skill when the user asks to run the workflow command `sprint-exps`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

**Input**：`sprint-xxx`（必填或可推断）；可选 `--dry-run`、`--focus`、`--skip-best-practices`

**Output**：Experience Analysis Report + `docs/knowledge-base/retrospectives/<sprint-id>-retrospective.md` + 可选 best-practices/incidents + 索引与 sprint.md 回链；复盘文档 MUST 包含“模型 Token 使用分析”与优化方案

**禁止**：`src/`、apply/archive、自动改 `rules/`

**推荐时机**：`/sprint-archive` 之后

---

## Steps

1. 运行或读取自动 Sprint Fact Sheet：
   ```bash
   python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary
   ```
2. 优先基于 Fact Sheet summary 构建 Sprint 概况、Scope、Change tasks、Issue 状态、验收摘要、warnings、AI usage 状态与 token risks；默认不得输出完整 `evidence_hints`。
   - 若 Sprint 包含 10+ Change，MUST 优先使用 summary 中的 `change_batches` 批次摘要构建复盘输入。
   - 成功路径只转述批次数、每批 Change 数、tasks 聚合计数、blocker/warning 数量与 recommended next read。
   - 仅当某批次出现 `needs_detail`、blocker、warning、missing 或 inconsistent 风险时，按 batch id 与 evidence hints 分段回读原始 `tasks.md` / `trace.md` 片段。
3. 运行归档路径残留检查，或使用 Fact Sheet 的 `archived_path_residuals`：
   ```bash
   python scripts/check-archived-path-residuals.py --sprint <sprint-id> --json
   ```
   若存在 `archived-path-residual` warning，Experience Analysis Report MUST 展示 residual path warning，复盘文档 MUST NOT 将旧路径作为新的证据链接写入。
4. 仅当 Fact Sheet summary 标记 `warnings`、`needs_detail`、缺失/不一致项，或用户指定 `--focus` / 明确要求证据时，使用字段模式读取完整 evidence hints 后分段回读对应原文片段：
   ```bash
   python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --fields evidence_hints
   ```
5. 构建 Token Usage Fact Sheet：优先使用自动 Fact Sheet summary 的 compact `ai_usage_snapshot`，包括 `fresh_gate`、`freshness_baseline`、`usage_matrices_summary`、关键 totals、warning_count 与 recommended_action；summary 默认不得消费或转述完整 `usage_matrices.rows`。只有当 `fresh_gate.status: pass`、`snapshot_status: present`、`ai_usage_mode: actual` 且 `usage_matrices_summary.available=true` 时，才可判断真实矩阵可用；此时复盘文档 MUST 优先通过专用 Markdown 渲染命令写入 sprint-015 风格表格：
   ```bash
   python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --ai-usage-markdown
   ```
   该输出必须包含 `Token Usage Fact Sheet` 与 `total_tokens`、`input_tokens`、`output_tokens`、`model_call_count` 四张矩阵。矩阵单元中的 `-` 表示该 workflow 阶段在当前 snapshot 中未采集或未归因，MUST NOT 被解读为真实 0；只有已观测 workflow 列中的数字 `0` 才表示真实零消耗。仅当需要调试渲染输入或字段兼容时，才 MAY 使用 `python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --fields ai_usage_snapshot.usage_matrices` 读取原始矩阵 JSON，原始矩阵列状态仍使用 `unknown` 表示未观测。若 fresh gate 为 `blocker`，或 snapshot `missing`、`stale`、`failed`、覆盖不足、关键 totals 为空或缺少矩阵摘要，MUST 先输出 fresh gate blocker、reason、impact、freshness_baseline 和 recommended_action，并要求刷新 snapshot 后再输出真实成本矩阵。若 recommended_action 指向 `scripts/extract-ai-usage.py` 或当前命令可运行 post-command hook，MUST 先刷新 snapshot；刷新完成后 MUST 重新运行 `python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary` 复核 fresh gate，且只能以刷新后的 summary 判断是否可渲染矩阵。不得沿用刷新前的 blocker 结论，也不得在未重新 summary 时直接运行 `--ai-usage-markdown` 写入真实矩阵。只有当用户明确要求继续 fallback 复盘时，才 MAY 输出 `ai_usage_mode: estimated_fallback` 的非量化成本风险分析；该输出 MUST 说明不能用于真实 token 成本量化，并保留 recommended_action。仅在需要定位原始证据时读取完整 evidence hints。
6. 五维分析：流程、需求设计、开发质量、可复用抽象、模型 Token 使用。
7. 聚类 → 行动项 → 写入 knowledge-base（除非 dry-run）。
8. 输出 Experience Analysis Report。

详见 `.agents/skills/sprint-exps/SKILL.md`。

---

## Fact Sheet 读取边界（MUST）

- MUST 先运行或读取 `scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary` 的输出，再决定是否读取 Sprint 四件套、Issue trace、OpenSpec Change 或 tasks 原文。
- MUST NOT 默认全文读取 sprint 四件套、全部 REQ/BUG/Change trace、review/root-cause/tasks。
- MUST NOT 在复盘中复制原始 trace、tasks、acceptance-report、OpenAPI、Orval generated 或测试日志全文；需要证据时只引用路径、聚合计数或短片段。
- MUST NOT 默认输出完整 `evidence_hints`；完整 evidence hints 只作为按需回读索引。
- MAY 按 Fact Sheet summary 的 `warnings` / `needs_detail` 回读对应文件片段，例如缺失 trace、状态残留、tasks 未完成、acceptance 结论不清晰；需要完整 evidence hints 时 MUST 使用 `python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --fields evidence_hints`。
- SHOULD 使用 `python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary` 做结构化核对，尤其是 `scope.counts`、`change_batches`、`warnings`、`token_risks`、`detail_triggers` 与 compact `ai_usage_snapshot`；summary 默认只包含 `usage_matrices_summary`，不得依赖完整 `usage_matrices.rows`。调试兼容问题时 MAY 使用 `--json`。
- For 10+ Change Sprint, SHOULD inspect `change_batches` before `changes[]` detail and MUST NOT default to reading every raw `tasks.md` or `trace.md`.
- MUST 检查 Fact Sheet 中的 `archived_path_residuals` 与 `archived-path-residual` warnings；如存在残留，只引用建议归档路径，不传播旧的 `iterations/change/<sprint-id>/` 或 active `openspec/changes/<change-id>/` 链接。

## 分析要点

- **模型 Token 使用分析（MUST）**：
  - 复盘文档 MUST 增加独立章节 `## 模型 Token 使用分析`，位置建议在“流程复盘”之后、“需求与设计”之前。
  - 优先使用 `data/ai-usage/sprints/<sprint-id>.json` 经 `scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary` 暴露的 compact 真实统计摘要：command run 数、模型调用、工具调用、失败重跑、input tokens、cached input tokens、output tokens、reasoning output tokens、total tokens、工具输出字符数，以及 `usage_matrices_summary` 的矩阵可用性、行列规模和 unknown 列数量。
  - 若 `ai_usage_snapshot.fresh_gate.status != pass`、`ai_usage_snapshot.snapshot_status != present`、`ai_usage_snapshot.ai_usage_mode != actual` 或 `ai_usage_snapshot.usage_matrices_summary.available != true`，MUST 输出 fresh gate blocker、reason（如 missing/stale/failed/coverage-missing/usage-matrices-missing/required-metrics-empty）、impact、freshness_baseline、recommended_action；默认不得生成真实 token 成本矩阵，不得编造具体 token 数字，不得静默按真实统计展示。
  - `usage_matrices_summary.raw_present=true` 只表示 snapshot 文件里存在原始矩阵，不代表可写入复盘；只有 `usage_matrices_summary.matrix_write_gate.status=pass` 且 `available=true` 才允许通过 `--ai-usage-markdown` 写入真实矩阵。
  - 若 snapshot 过期、覆盖不足、缺少矩阵或无法判定覆盖范围，MUST 在本章节保留 warning，并提示刷新 snapshot；覆盖不足或缺少矩阵 MAY 保持 `snapshot_status: present`，但 fresh gate MUST 为 blocker 且 `ai_usage_mode` MUST NOT 作为真实统计使用。仅当用户明确要求继续 fallback 复盘时，MAY 输出 `ai_usage_mode: estimated_fallback` 的非量化成本风险分析，且 MUST 说明不能用于真实 token 成本量化。
  - 当 compact summary 显示 `usage_matrices_summary.available=true` 且确需写入矩阵表时，MUST 通过 `--ai-usage-markdown` 生成可直接写入复盘文档的表格章节；复盘文档 MUST 在 `## 模型 Token 使用分析` 中新增四张指标矩阵表，数据来源为 `data/ai-usage/sprints/<sprint-id>.json` 经 Fact Sheet 渲染输出：
    - 第一张：总 Token 消耗数 `total_tokens`。
    - 第二张：总输入 Token 消耗数 `input_tokens`。
    - 第三张：总输出 Token 消耗数 `output_tokens`。
    - 第四张：模型调用次数 `model_call_count`。
  - 四张矩阵表 MUST 使用相同结构：第一列为对象，表格最上方 MUST 是 `Total` 汇总行；之后纵向按 Sprint、REQ、BUG 排列（例如 `sprint-010` / `REQ-0001-*` / `BUG-0001-*`，展示时 MAY 保留 canonical ID）；横向命令列 MUST 按 `Capture`、`BUG-Capture`、`REQ-Capture`、`BUG-Explore`、`REQ-Explore`、`REQ-Generate`、`BUG-Generate`、`REQ-Complete`、`BUG-Complete`、`REQ-Review`、`BUG-Review`、`REQ-Opsx`、`BUG-Opsx`、`Opsx-Explore`、`Opsx-Propose`、`Opsx-Apply`、`Opsx-Modify`、`Opsx-Archive`、`Sprint-Propose`、`Sprint-Explore`、`Sprint-Apply`、`Sprint-Archive` 展示。
  - 矩阵口径 MUST 说明：`Total` 与 Sprint 行按唯一 command run 汇总；REQ/BUG 行是对象归因视图，同一 command run 关联多个 REQ/BUG 时可在多个对象行出现，因此对象行不应直接相加后与 `Total` 比较；`-` 表示对应 workflow 列未观测，不等价于真实 `0`。
  - MUST 分析高消耗来源：重复读取 `rules/` 与技能文件、宽泛 `rg/find`、全量 Sprint/Issue/Change 读取、`openspec/archive/**`、legacy `openspec/changes/archive/**`、OpenAPI/Orval 生成物 diff、长测试日志、Workflow Sync 全量输出、Docker/build 大日志、Harness/模板 assets 注入。
  - MUST 优先引用自动 Fact Sheet summary 的 `token_risks`、Change/tasks 计数、四件套行数、warnings 与 evidence hint 计数，减少人工展开四件套、trace 与 tasks 的 token 消耗。
  - MUST 给出优化方案，至少包含：读取边界、搜索排除、输出截断、diff/stat 优先、失败日志摘要、复用已读规则摘要、按 Change 分段处理、必要时沉淀脚本或校验 gate。
  - MUST 将可执行优化项写入行动项表，建议下一命令可用 `/req-capture`、`/bug-capture`、`/opsx-propose` 或下一 Sprint 的 `/sprint-propose`。
  - SHOULD 对照 `rules/agent-context-budget.md`，指出本 Sprint 哪些行为符合预算规则、哪些行为需要修正。
- **重复 BUG**：UI 不一致、上传、登录等模式 → 预防建议 + 是否 best-practice
- **需求文档**：缺原型/acceptance 与 fix-* 数量的关联
- **组件抽象**：多 REQ 相似页面 → AdminListPage / 共享弹窗等建议
- **流程**：review/opsx/apply/archive 卡点与容量

行动项含优先级与下一命令（`/req-capture`、`/sprint-propose` 等）。

## Token 使用章节模板

```markdown
## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据/说明 |
|------|----|-----------|
| 精确 token 统计 | 有 / 无 | 来源：会话元数据 / 工具日志 / 无法获取 |
| AI usage mode | actual / estimated_fallback | Fact Sheet: `ai_usage_snapshot.ai_usage_mode` |
| Snapshot status | present / missing / stale / failed | Fact Sheet: `ai_usage_snapshot.snapshot_status` |
| Fresh gate | pass / blocker | Fact Sheet: `ai_usage_snapshot.fresh_gate.status` |
| Freshness baseline | 待填 | Fact Sheet: `ai_usage_snapshot.freshness_baseline` |
| 主要输入消耗 | 待填 | 例如规则重复读取、Sprint 四件套、Issue/Change trace |
| 主要输出消耗 | 待填 | 例如测试日志、Workflow Sync 报告、diff 输出 |
| 重复/浪费来源 | 待填 | 例如同一规则多次全量读取、宽泛搜索命中过多 |
| 已采用节省策略 | 待填 | 例如 `rg --files` 定位、`sed -n` 分段、`git diff --stat` |

### total_tokens 矩阵

| 对象 | Capture | BUG-Capture | REQ-Capture | BUG-Explore | REQ-Explore | REQ-Generate | BUG-Generate | REQ-Complete | BUG-Complete | REQ-Review | BUG-Review | REQ-Opsx | BUG-Opsx | Opsx-Explore | Opsx-Propose | Opsx-Apply | Opsx-Modify | Opsx-Archive | Sprint-Propose | Sprint-Explore | Sprint-Apply | Sprint-Archive |
|------|---------:|------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|-----------:|-----------:|---------:|---------:|-------------:|-------------:|-----------:|------------:|-------------:|---------------:|---------------:|-------------:|---------------:|
| Total | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- |
| sprint-xxx | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- | 待填/- |

### input_tokens 矩阵

同上结构，指标取 `input_tokens`。

### output_tokens 矩阵

同上结构，指标取 `output_tokens`。

### model_call_count 矩阵

同上结构，指标取 `model_call_count`。

> 矩阵数据优先来自 `python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --ai-usage-markdown`；summary 只提供 `usage_matrices_summary`。若完整矩阵缺失，提示刷新 `data/ai-usage` snapshot，不得手工估填具体数值；若单元格为 `-`，说明该 workflow 阶段未采集或未归因，不得当作真实 0。

### 高消耗来源

| 来源 | 影响 | 证据 | 优化方案 |
|------|------|------|----------|
| 待填 | high / medium / low | 文件、命令或 trace | 具体做法 |

### 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|----|--------|------|------------|------|
| T-001 | P1 | 待填 | `/req-capture` 或 `/bug-capture` | open |
```

## Final Step — AI Usage Post-command Hook (MUST)

After the retrospective output is completed and any required Workflow Sync or index updates have succeeded, run:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event sprint.exps --sprint <sprint-id> --json
```

- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.

## Final Output Contract（MUST）

命令结束前，最终回复必须包含面向用户的真实结果，不得输出本段规则、尖括号占位符、MUST/SHOULD 规范语句或与当前命令无关的通用示例。

输出必须包含两项：

- `下一步`：写真实、可复制的下一条命令；若当前没有可推进动作，写“暂无可推进下一步”。
- `待用户决策/处理`：没有额外人工事项时写“无”；否则只列具体的缺失输入、范围/策略选择、证据补充、验收确认、发布确认、生产实施确认、阻塞项或人工处理事项。

输出判定：

- 有唯一可执行下一步时，`下一步` 写真实命令；若无额外人工事项，`待用户决策/处理` 写“无”。
- 下一步被用户选择、补证、验收、发布确认、生产实施确认或阻塞项卡住时，`下一步` 写“暂无可推进下一步”，并在 `待用户决策/处理` 列出具体阻塞事项。
- 已有下一步且仍有额外人工事项时，`待用户决策/处理` 只列命令之外的事项，不得重复 `下一步` 中的命令或动作。
- REQ 链路使用完整原始 `REQ-*`；BUG 链路使用完整原始 `BUG-*`；非 REQ/BUG 的直接 Change 才使用真实 Change ID。
- 不得因为输出了下一步引导而自动执行下一命令；除非用户明确授权。
