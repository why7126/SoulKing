---
name: "opsx-apply"
description: "Implement tasks from an OpenSpec change"
---

# opsx-apply

Use this skill when the user asks to run `/opsx-apply <target>` or implement an OpenSpec change. `<target>` can be `REQ-*`, `BUG-*`, or a raw OpenSpec `<change-id>`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- 大 diff 先用 `git diff --stat` / `git diff --name-only`；不得默认展开 `docs/generated/openapi.json`、生成产物、coverage 或构建产物全文。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- `openspec instructions apply --json` returned `contextFiles` is the default read boundary.
- UI/test定位先 `rg -l` 找文件，再分段读取目标片段。
- 默认排除 generated、node_modules、coverage、dist、archive 大目录。
- best-practices 只读 Cross-cutting Gate 命中的标签文件。
- 完成一组 task 后用 `git diff -- <changed-files>` 或 `tasks.md` 片段复核，避免重复读全部上下文。
- 命令输出优先 `max_output_tokens <= 8000`。

## Input

- `<target>`：指定 REQ、BUG 或 Change。
- Omitted：若上下文唯一可推断则使用；否则列 active changes 并询问。
- `--skip-cross-cutting-gate`：仅 P0 热修可跳过，输出必须说明理由。

## Target Resolution（MUST）

Resolve `<target>` before reading OpenSpec artifacts, and keep both identifiers:

| Input | Resolution | User-facing target |
|---|---|---|
| `REQ-*` | Read `issues/requirements/<REQ-full-id>/trace.md` and use the latest non-archived `openspec_changes[].change_id` | Continue referring to the original `<REQ-full-id>` |
| `BUG-*` | Read `issues/bugs/<BUG-full-id>/trace.md` and use the latest non-archived `openspec_changes[].change_id` | Continue referring to the original `<BUG-full-id>` |
| other | Treat as raw OpenSpec `<change-id>` | Use the change id |

If a `REQ-*` / `BUG-*` has zero or multiple eligible active changes, stop and ask for the exact target. All OpenSpec CLI commands below use `<resolved-change-id>`. Final next steps MUST preserve the original issue target when present, for example `/opsx-archive <REQ-full-id>` or `/opsx-archive <BUG-full-id>`；也就是完整 `REQ-xxxx-slug` / 完整 `BUG-xxxx-slug`。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/coding.md
rules/testing.md
rules/security.md
rules/directory-structure.md
rules/document-governance.md
rules/requirement-management.md
rules/bug-management.md
rules/root-cause-evidence.md（BUG 来源或涉及根因判断时）
rules/iterations-lifecycle.md
.agents/skills/workflow-sync/SKILL.md
```

Then run:

```bash
openspec status --change "<resolved-change-id>" --json
openspec instructions apply --change "<resolved-change-id>" --json
```

Read every concrete path in `contextFiles`.

When relevant, read focused snippets from:

```text
issues/requirements/<REQ>/acceptance.md + trace.md
issues/bugs/<BUG>/root-cause.md + acceptance.md + trace.md
iterations/change|archive/<sprint>/sprint.md §横切预防清单
docs/knowledge-base/best-practices/<matched>.md
```

For BUG-sourced Changes or fixes that involve root-cause claims, MUST read `rules/root-cause-evidence.md` and verify that `root-cause.md` uses `unknown` / `hypothesis` / `probable` / `confirmed` semantics. A `confirmed` root cause without evidence is a blocker until the BUG document is completed or the implementation explicitly records the remaining evidence risk.

## Sprint Inclusion Gate（MUST before implementation）

Before editing `app/`, `app/static/`, running implementation checks, or marking any task complete, verify the target Change is eligible for `/opsx-apply`.

For every Change:

1. Identify linked `REQ-*` / `BUG-*` from Change trace, proposal/design, tasks, or Issue `trace.md` `openspec_changes[]` when present.
2. Confirm `python scripts/sync-workflow-status.py --event opsx.apply --change <resolved-change-id> --sprint auto --dry-run` resolves a Sprint and does not report sprint skipped/unresolved.
3. Read the resolved `iterations/change|archive/<sprint>/sprint.yaml` snippet and confirm `changes[]` contains `<resolved-change-id>`.
4. For linked issues, confirm `requirements[]` contains linked `REQ-*` and/or `bugs[]` contains linked `BUG-*`.
5. For linked issues, confirm each linked Issue `trace.md` has `iteration: <sprint-id>` and `status: in_sprint` or a later delivery state.

If any check fails, **BLOCKED**: do not implement. If the linked REQ/BUG is already in a Sprint but `changes[]` lacks `<change-id>`, first run the originating `/req-opsx` or `/bug-opsx` Workflow Sync final step again to repair Sprint scope, then rerun this dry-run gate. Tell the user to run `/sprint-propose` only when the linked REQ/BUG itself is not in any Sprint scope.

If the user already ran `/sprint-propose` for the linked REQ/BUG but the dry-run still reports `change <id> not in sprint scope`, treat this as Sprint scope machine-source persistence failure, not as missing user intent. Repair `iterations/change|archive/<sprint>/sprint.yaml` with:

```bash
python scripts/add-sprint-scope-item.py \
  --sprint <sprint-id> \
  [--req <REQ-id> | --bug <BUG-id>] \
  --change <change-id> \
  --size <XS|S|M|L|XL|XXL> \
  --story-points <number> \
  --person-days <number> \
  --rationale "<估算与影响说明>"
```

Then rerun Workflow Sync, `validate-sprint-scope.py`, and this apply dry-run gate. Do not ask the user to repeat the same `/sprint-propose` command when the issue/change pair and target Sprint are already known.

No Change may bypass this Sprint Inclusion Gate merely because it has no linked `REQ-*` / `BUG-*`.

## Cross-cutting Apply Gate（MUST before `src/`）

Skip only with `--skip-cross-cutting-gate` and explicit P0/hotfix reason.

Infer tags from trace, proposal/design, change id, and tasks:

| Tag | Trigger | Best-practice |
|---|---|---|
| `admin-list` | 管理端列表、分页、table-card | `admin-list-page-consistency.md` |
| `admin-form` | 表单页、设置页、保存 CTA | `admin-form-page-consistency.md` |
| `admin-modal` | 弹窗 CRUD / modal fix | `admin-modal-width-css-cascade.md` |
| `media-upload` | 图片、视频、Logo、头像上传 | `admin-media-upload-chain.md` |

Report:

```text
Change / Tags / Refs
AC-XCUT: pass|warn|n/a
knowledge_base_refs: pass|warn|n/a
best-practices read: pass|n/a
Verdict: PROCEED | WARN-PROCEED | BLOCKED
```

BLOCKED if add-* UI lacks required cross-cutting AC. Do not edit `src/` until resolved.

## 产品数据采集与链路观测门禁（MUST before implementation）

Before implementation, if the Change touches API, DB, audit logs, usage events, playback/download, media import, Task Trace, frontend request wrapper, admin request wrapper, or object storage observability, MUST read `docs/standards/product-data-collection-observability.md` and confirm the Change has `product_data_collection_observability` with `affected_layers`, `reason`, and `validation`.

When the Change declares `status: not_applicable`, the N/A reason MUST explain why API, DB, request logs, usage events, Task Trace, request wrappers, media pipeline, or object storage are not affected. If the declaration is missing or vague, run `python scripts/validate-product-data-observability-gates.py --change <change-id>` and fix the Change artifacts before editing implementation files.

## Implementation Loop

For each pending task:

1. Announce current task.
2. Make minimal scoped changes.
3. Add/update tests when behavior changes.
4. Mark task `- [ ]` → `- [x]` immediately after completion.
5. Re-run focused checks/tests.
6. Stop and ask if task is ambiguous, gate is blocked, or implementation reveals design conflict.

When updating `tasks.md`, preserve Chinese-first wording required by `rules/language.md`; task text MUST NOT be rewritten into English-only descriptions while marking checkboxes.

## Completion Output

Report change id, schema, completed tasks this session, total progress, tests/checks run, remaining tasks, and whether archive is ready.

## Final Step — Workflow Sync（MUST）

Before Workflow Sync, run:

```bash
python scripts/validate-openspec-language.py
```

- Exit code MUST be `0`；若失败，先修正 active Change 文档中的英文脚手架标题或全英文任务项。

Run:

```bash
python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto
```

- Exit code MUST be `0`。
- Print summary Workflow Sync Report；use `--output detail` only for debugging。
- Verify linked REQ/BUG trace has `openspec_changes[].status: applied` and `/opsx-apply` in `## 变更记录`; if missing, fix workflow sync and rerun instead of hand-editing marker blocks.
- Verify linked REQ/BUG `acceptance.md` has `acceptance_status: pending` or equivalent `## 验收结果回填` with `source_change` and resolved Sprint; if missing, rerun Workflow Sync or use `--scan-issue-subdocuments --dry-run` to diagnose.
- Do not hand-edit workflow-sync marker blocks。

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync exits with code `0`, run:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change <change-id> --sprint <resolved-sprint-id> --json
```

- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- Use the Sprint resolved by Workflow Sync; do not pass the literal value `auto` to `extract-ai-usage.py`.
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
