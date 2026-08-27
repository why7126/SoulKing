---
name: "sprint-apply"
description: "按 Sprint 依赖与优先级编排 OpenSpec Change 开发"
---

# sprint-apply

Use this skill when the user asks to run `/sprint-apply <sprint-id>`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- Sprint apply 必须逐 Change 聚焦读取，不得把整个 Sprint 历史、全部 issue 包或全部 active changes 同时装入上下文。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 先读 `sprint.yaml` 与必要 trace/status 片段，不全量读取 Sprint 四件套。
- 每个 Change 只读 `proposal.md`、`tasks.md`、依赖字段和必要 design/spec 片段。
- UI gate 只读取命中标签的 best-practices。
- Queue report 输出摘要；大 diff/test 输出分段读取。

## Input

- `<sprint-id>` required unless only one active Sprint exists.
- Flags: `--dry-run`、`--parallel`、`--force-req-check`、`--skip-cross-cutting-gate`（仅 P0 热修）。

## 产品数据采集与链路观测门禁

对队列中涉及 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测的 Change，MUST 确认已读取 `docs/standards/product-data-collection-observability.md`，且存在 `product_data_collection_observability` 适用层级、N/A 原因、`reason` 和 `validation` 验证计划。

缺少声明时不得把该 Change 标为 ready；可运行 `python scripts/validate-product-data-observability-gates.py --change <change-id>` 定位缺失项。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/testing.md
rules/requirement-management.md
rules/bug-management.md
rules/iterations-lifecycle.md
rules/directory-structure.md
.agents/skills/workflow-sync/SKILL.md
iterations/change|archive/<sprint>/sprint.yaml
```

Focused snippets as needed:

```text
iterations/<stage>/<sprint>/sprint.md §目标/Scope/依赖/横切预防清单
issues/requirements|bugs/<stage>/<id>/trace.md
openspec/changes/<change>/proposal.md + tasks.md + trace.md
```

## Gates

### Review Gate（MUST）

All Sprint REQ/BUG in formal scope MUST be `approved` or `in_sprint`. If not, stop and report remediation; do not apply related changes.

### Change Status Gate

| Status | Action |
|---|---|
| archived | skip |
| all tasks complete | skip or suggest archive |
| blocked / missing artifacts | pause |
| active with pending tasks | eligible |

### Cross-cutting Gate

Before editing `src/`, run the same gate as `.agents/skills/opsx-apply/SKILL.md` for each APPLY NEXT change.

## Queue Algorithm

1. Resolve Sprint directory via lifecycle rules.
2. Load `requirements[]`、`bugs[]`、`changes[]` from `sprint.yaml`.
3. Map each Change to related REQ/BUG and priority.
4. Build dependencies from proposal/design/tasks/trace and Sprint dependency section.
5. Sort: P0 BUG > P0 REQ > P1 > P2; prerequisites before dependents.
6. Output Sprint Queue Report before changing files.

Queue Report MUST include:

```text
Sprint / status / lifecycle_stage
Eligible changes
Skipped changes + reason
Blocked changes + reason
Topological order
Next APPLY target
```

`--dry-run` stops after Queue Report.

## Execution Loop

For each eligible Change:

1. Announce APPLY target.
2. Execute `/opsx-apply` equivalent using `.agents/skills/opsx-apply/SKILL.md`.
3. Run focused tests/checks.
4. Update tasks and trace.
5. Continue until queue exhausted, blocked, or user interrupts.

Do not archive automatically unless user explicitly asks for sprint/archive flow.

## Output

Report completed changes, skipped/blocked items, tests/checks, Sprint progress, and next suggested command.

## Final Step — Workflow Sync（MUST）

Run:

```bash
python scripts/sync-workflow-status.py --event sprint.apply --sprint <sprint-id>
```

- Exit code MUST be `0`。
- Print summary Workflow Sync Report；use `--output detail` only for debugging。
- Do not hand-edit workflow-sync marker blocks。

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync exits with code `0`, run:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event sprint.apply --sprint <sprint-id> --json
```

- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.

## Final Output Contract（MUST）

命令结束前，最终回复必须包含面向用户的真实结果，不得输出本段规则、尖括号占位符、MUST/SHOULD 规范语句或与当前命令无关的通用示例。

输出判定：

- `下一步`：写真实、可复制的下一条命令；若当前没有可推进动作，写“暂无可推进下一步”。
- `待用户决策/处理`：没有额外人工事项时写“无”；否则只列具体的缺失输入、范围/策略选择、证据补充、验收确认、发布确认、生产实施确认、阻塞项或人工处理事项。

去重规则：

- 有唯一可执行下一步时，`下一步` 写真实命令；若无额外人工事项，`待用户决策/处理` 写“无”。
- 下一步被用户选择、补证、验收、发布确认、生产实施确认或阻塞项卡住时，`下一步` 写“暂无可推进下一步”，并在 `待用户决策/处理` 列出具体阻塞事项。
- 已有下一步且仍有额外人工事项时，`待用户决策/处理` 只列命令之外的事项，不得在「待用户决策/处理」中重复 `下一步` 中的命令或动作。

不得因为输出了下一步引导而自动执行下一命令；除非用户明确授权。
