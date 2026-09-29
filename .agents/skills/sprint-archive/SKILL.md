---
name: "sprint-archive"
description: "批量归档 Sprint 内 OpenSpec Change 并关闭迭代"
---

# sprint-archive

Use when the user asks `/sprint-archive <sprint-id>` or wants to close a Sprint.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- Start from `sprint.yaml`; do not full-read Sprint four-piece unless closing fields are needed.
- For each Change, read only `tasks.md`, trace/status, and delta headings.
- Reuse `.agents/skills/opsx-archive/SKILL.md`; do not duplicate full archive reasoning.
- `--dry-run` must stop after queue/readiness report.

## Input

- `<sprint-id>` preferred; if omitted, infer only when one active Sprint exists.
- Flags: `--dry-run`、`--change <change-id>`、`--force`、`--skip-sync`（不推荐）、`--no-sprint-close`。

## Must Read / Run

```text
AGENTS.md
rules/document-governance.md
rules/directory-structure.md
rules/iterations-lifecycle.md
.agents/skills/opsx-archive/SKILL.md
.agents/skills/workflow-sync/SKILL.md
iterations/change/<sprint-id>/sprint.yaml
iterations/change/<sprint-id>/sprint.md（依赖/Scope 片段）
```

```bash
openspec list --json
python scripts/validate-sprint-archive-readiness.py --sprint <sprint-id>
python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --json
```

`validate-sprint-archive-readiness.py` includes the Sprint close stale scan. It MUST fail when Sprint four-piece docs or scoped REQ/BUG top-level Markdown files still contain stale intermediate wording such as "待 `/req-opsx`", "待 `/bug-opsx`", "待 `/opsx-apply`", stale `proposed` / `applied` semantics for archived Changes, unresolved `待开发` / `待实现` / `待验收`, active Change paths for archived Changes, or canonical `openspec/changes/archive/` links. For focused diagnosis, run:

```bash
python scripts/check-sprint-close-stale-scan.py --sprint <sprint-id>
```

Do not hand-edit `sprint.md` workflow-sync marker blocks while fixing stale scan blockers; rerun Workflow Sync or edit only non-derived human-authored notes.

For a Sprint with 10+ Change ids in `sprint.yaml`, first inspect the machine-readable `change_batches` from readiness / Fact Sheet JSON before reading raw Change files. Use batch summary counts, blockers, warnings and evidence hints to decide which `tasks.md` or `trace.md` snippets need detail. Successful output MUST stay compact: report total changes, batch count, archived/skipped/blocked counts, warning count and recommended next read; do not print full batch JSON or every raw tasks/trace detail.

For single change mode:

```bash
python scripts/validate-sprint-archive-readiness.py --sprint <sprint-id> --change <change-id>
```

Readiness distinguishes active and archived Change semantics: active Changes are checked for directory/tasks completion; archived Changes are additionally rechecked for `trace.md`. If an archived Change lacks `trace.md`, `proposal.md`、`design.md` or `tasks.md` MUST contain a complete `## 归档验证摘要` covering validation command/result, acceptance verdict, Issue/Sprint status, and archive path/time evidence. This is a Sprint-level secondary gate; new single Change archives are expected to catch the same evidence gap during `/opsx-archive`.

Ignored, untracked local env files (`.env`, `.env.*`, `deploy/local/*.env`, `deploy/prod/*.env`, `scripts/build-images.env`) are allowed to exist and MUST NOT block Sprint archive by existence alone. Block only when a real env file is Git-tracked, outside approved local env paths, or its contents appear in release, Mintlify, archive evidence, AI Usage, logs or replies.

## 产品数据采集与链路观测归档门禁（MUST）

关闭 Sprint 前，若 Sprint 范围内存在 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测相关 REQ、BUG 或 Change，MUST 读取 `docs/standards/product-data-collection-observability.md`，并复核 `product_data_collection_observability` 适用性、`affected_layers` 适用层级、N/A 原因、`reason`、`validation` 验证摘要和验收结果。

建议运行 `python scripts/validate-product-data-observability-gates.py --sprint <sprint-id>`；失败时必须先补齐声明字段、N/A 原因或验收证据。

Before any issue package is moved to `issues/**/archive/`, the promote step MUST pass the issue subdocument status gate:

```bash
python scripts/promote-issues-for-archive.py --sprint <sprint-id>
```

If scoped REQ/BUG child Markdown files still contain non-closed frontmatter or fenced YAML `status` values such as `draft`、`pending_review`、`in_sprint`、`applied`、`todo`、`open`, keep the Sprint close blocked until those documents are reconciled.

If readiness returns non-zero or `Verdict: BLOCKED`, stop unless user explicitly passed `--force` and confirms each blocker.

## Queue Rules

1. Only archive Change ids listed in `sprint.yaml`.
2. Skip already archived changes and record path.
3. Block by default when tasks/artifacts are incomplete, `tasks.md` is missing, change dir is missing, or MODIFIED title cannot be matched.
4. Sort dependencies as in sprint apply: base `add-*` before dependent `fix-*` / `update-*`; unrelated changes keep `sprint.yaml` order.
5. Output Sprint Archive Queue Report before moving anything.

Queue Report MUST include Sprint, mode, readiness verdict, each change action (`SKIP` / `ARCHIVE NEXT` / `QUEUE` / `BLOCKED`), blockers, and warnings.

## AI Usage Snapshot Gate（MUST before Close Sprint）

Before the final close step, check the Sprint AI usage snapshot through the Fact Sheet:

```bash
python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --json
```

Inspect `ai_usage_snapshot.fresh_gate`、`snapshot_status`、`ai_usage_mode`、`generated_at`、`coverage`、`warnings` and `recommended_action`.

- If `fresh_gate.status: pass`, `snapshot_status: present` and `ai_usage_mode: actual`, output only a compact summary: fresh gate status, snapshot status, mode, path, generated_at, coverage status, usage_matrices presence and warning_count.
- If snapshot is `missing`、`stale`、`failed`、`estimated_fallback` or has coverage/matrix blockers, try to generate/refresh it only when the operator provides a local session input. If automatic attribution cannot identify the target command turns, require a local manual map keyed by `turn_hash` or `source_session_hash`:

```bash
python scripts/extract-ai-usage.py --session-jsonl <local-session.jsonl> --manual-map <manual-map.json> --sprint <sprint-id> --json
python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary
```

- The manual map may include `requirements`、`bugs`、`changes`、`sprint_id`、`workflow_event`、`release_sprints`、`release_version`、`post_command_target` and `attribution_confidence`. After refresh, MUST use the new Fact Sheet summary to re-check `fresh_gate`、`snapshot_status`、`ai_usage_mode`、coverage、totals and `usage_matrices_summary`; do not reuse pre-refresh conclusions.
- If local session input is unavailable or generation fails, continue only with an explicit warning in the close report: `ai_usage_mode: estimated_fallback`, reason, impact, and recommended_action. Do not state that real token usage was used.
- Do not print raw session JSONL, prompts, system/developer instructions, local absolute paths, tool output bodies, or full snapshot contents.

## Archive Loop

For each `ARCHIVE NEXT`:

1. Execute `/opsx-archive` equivalent using `.agents/skills/opsx-archive/SKILL.md`.
2. Prefer `openspec archive "<change-id>" -y`; use manual fallback only with delta self-check.
3. Stop the whole Sprint archive on title mismatch, archive target conflict, failed sync/promote script, or user interruption.

## Close Sprint

Unless `--no-sprint-close`, close only when all Sprint changes are archived and readiness passes without `--force`:

```bash
python scripts/validate-sprint-archive-readiness.py --sprint <sprint-id>
```

Then update the four-piece as needed:

```text
sprint.yaml: status completed, lifecycle_stage archive
acceptance-report.md: final verdict/date/check summary
release-note.md: draft -> published if applicable
sprint.md: closure note only outside workflow-sync marker blocks
```

Move directory with `git mv iterations/change/<sprint-id> iterations/archive/<sprint-id>`.

## Archived Path Residual Gate（MUST after Close Sprint）

After the Sprint directory has moved to `iterations/archive/<sprint-id>/` and Workflow Sync / issue promotion have succeeded, run:

```bash
python scripts/check-archived-path-residuals.py --sprint <sprint-id>
python scripts/check-sprint-close-stale-scan.py --sprint <sprint-id>
```

- Exit code `0` means no stale `iterations/change/<sprint-id>/` or active `openspec/changes/<change-id>/` references were found in this Sprint scope.
- Exit code `1` MUST block a silent success close-out. Report the file, line, old path, suggested path, and exact retry command from the residual report.
- The check scope MUST come from `sprint.yaml` requirements / bugs / changes and Sprint four-piece documents; do not broad-scan all `issues/**`, `openspec/archive/**`, or legacy `openspec/changes/archive/**`.
- The stale scan MUST also pass before close-out; report blocker severity, kind, target, file, line and retry command when it fails.
- Do not hand-edit workflow-sync marker blocks while fixing residual links.

## Final Step — Workflow Sync（MUST）

```bash
python scripts/sync-workflow-status.py --event sprint.archive --sprint <sprint-id>
```

Exit code MUST be `0`; print summary Workflow Sync Report; use `--output detail` only for debugging.

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync exits with code `0`, run:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event sprint.archive --sprint <sprint-id> --json
```

- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.

## Output

Report archived/skipped/blocked counts, Sprint close status, updated files, validation commands, archived path residual check summary, and exact retry command if paused.

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
