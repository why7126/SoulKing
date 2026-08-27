---
name: "req-opsx"
description: "已评审需求 → OpenSpec Change（CLI 驱动）；原 /requirement-to-opsx"
---

# req-opsx

Use this skill when the user asks to run the workflow command `req-opsx`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- REQ 转 Change 时只读取目标 REQ 六件套摘要与候选 spec 片段；不得默认读取全部 `openspec/specs/**`。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

将 **`approved`** 的 `issues/requirements/REQ-*` 转为 `openspec/changes/<change-id>/`（proposal / design / specs / tasks）。**不写 `src/`**；实现用 `/opsx-apply`。

**Input**：`REQ-xxxx` 或 `REQ-xxxx-name`

| Flag | 含义 |
|------|------|
| `--type add\|fix\|update` | 强制 change 类型 |
| `--strategy <name>` | css-port、tailwind-ds 等 |
| `--skip-explore` | 跳过 UI 策略探讨 |
| `--change-name <kebab-case>` | 指定 change id |

---

## 前置关系

```text
/req-capture → /req-explore → /req-generate → /req-complete → /req-review (approved)
        │
        └─ /req-opsx REQ-*  →  /opsx-apply  →  /opsx-archive
```

---

## Step 0 — 必须读取

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/requirement-management.md
rules/ui-design.md
rules/testing.md
rules/directory-structure.md
```

```bash
openspec list --json
openspec list --specs
```

REQ 目录：requirement.md、user-stories.md、business-flow.md、acceptance.md、trace.md、prototype/**

---

## Step 0.5 — 评审门禁（MUST — 无例外）

读 `trace.md`（或 requirement.md frontmatter）`status`：

| status | 动作 |
|--------|------|
| `approved` | **立即停止** → `/sprint-propose --req <REQ-full-id>` |
| `in_sprint` | 可继续（须已完成 `/req-review` 与 Sprint 纳入） |
| `done` | 可继续（追溯/补建 change） |
| `pending_review` / `draft` / `captured` / `enriching` / … | **立即停止** → `/req-review REQ-xxxx` |

未评审 **不得** opsx；`status: in_sprint` 是创建 Change 的默认准入状态。不得因 Sprint 规划已写入而 bypass（见 `rules/requirement-management.md`）。

---

## Step 1 — Readiness

输出 **Requirement Readiness Report**（ready / partially ready / not ready）。

**Not Ready** → `/req-complete REQ-xxxx`，**停止**，不创建 change。

---

## Step 2 — 影响分析与 Change 分类

```yaml
impact: { backend, web, miniapp, admin, database, storage, api }
capabilities: { new: [], modified: [] }
```

| 条件 | change_type | 示例 |
|------|-------------|------|
| 无相关 spec | add | add-user-login |
| 已有实现，验收/视觉未过 | fix | fix-login-css-port |
| 仅规范文案 | update | update-login-acceptance-sync |

---

## Step 3 — 原型与验收冲突（MUST）

`prototype/web/` 存在时输出 Conflict Report；优先级：

```text
HTML > PNG > *-context.md > acceptance.md > ui-design.md > openspec/specs
```

design.md **MUST** 含 Conflict Resolution；delta spec 用 MODIFIED/REMOVED 消化。

---

## Step 3.5 — 产品数据采集与链路观测门禁（MUST）

若 REQ 或目标 Change 涉及 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测，MUST 读取 `docs/standards/product-data-collection-observability.md`，并在 `design.md`、`trace.md`、`acceptance.md` 或 `tasks.md` 写入 `product_data_collection_observability` 固定声明，至少包含 `status`、`affected_layers`、`reason` 和 `validation`。

N/A 声明必须说明为什么不影响 API、DB、请求日志、行为事件、Task Trace、端请求封装、媒体链路或对象存储；不得只写“无”或“不涉及”。后续 `/opsx-apply` 前 SHOULD 运行 `python scripts/validate-product-data-observability-gates.py --change <change-id>`。

---

## Step 4 — UI Explore Gate

`impact.web` 且有 prototype 时，无 `--strategy` 且非 `--skip-explore`：选 CSS Port / DS / Asset，写入 design.md D1。

---

## Step 5 — 创建 Change（CLI）

```bash
openspec new change "<change-id>"
openspec status --change "<change-id>" --json
```

---

## Step 6 — 生成 Artifacts

```bash
openspec instructions <artifact-id> --change "<change-id>" --json
```

按 schema 顺序写 proposal、design、specs、tasks。MODIFIED 标题 **MUST** 与 `openspec/specs/` 一致。

---

## Step 7 — 追溯

更新 REQ `trace.md`：

```yaml
openspec_changes:
  - change_id: …
    type: fix
    status: proposed
```

创建 `openspec/changes/<id>/trace.md`（UI 类含 PNG checklist）。

---

## Step 8 — 输出

```text
## Req → OpenSpec 完成
**REQ:** …
**Change:** …
**Next:** 若 Workflow Sync 已解析到 Sprint：`/opsx-apply <REQ-full-id>` 或 `/sprint-apply sprint-xxx`；若未解析到 Sprint：先 `/sprint-propose --req <REQ-full-id>`
```

---

## Guardrails

| 规则 | 说明 |
|------|------|
| 仅 approved | 未评审不得 opsx |
| 不替代 req-complete | 文档不全先 complete |
| 不跳过 CLI | 禁止手写 change 目录 |
| 不写 src | 实现用 opsx-apply |

---

## 参考

- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`、`opsx-archive.md`、`opsx-explore.md`
- 归档样例：`openspec/archive/`

---

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event req.opsx --req <REQ-id> --change <change-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- 当目标 REQ 已在 Sprint 正式范围内时，Workflow Sync **MUST** 把 `<change-id>` 写入同一 Sprint 的 `changes[]`，同步 `scope_estimates[].change`，并移除对应 open-change 延后项；结束前用 `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run` 确认后续 `/opsx-apply` 不再报告 `change <id> not in sprint scope`。
- 最终下一步若指向 `/opsx-apply`，MUST 使用原始 `<REQ-full-id>`，也就是完整 `REQ-xxxx-slug`，由 `/opsx-apply` 自行解析到目标 Change；避免丢失需求语境。
- 若 dry-run 报告 `change <id> not in sprint scope`，且 REQ 已在某个 Sprint 中，MUST 先用 `python scripts/add-sprint-scope-item.py --sprint <sprint-id> --req <REQ-id> --change <change-id> --size <XS|S|M|L|XL|XXL> --story-points <number> --person-days <number> --rationale "<估算与影响说明>"` 修复 Sprint 机器源，再重跑 Workflow Sync 和 dry-run。
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync exits with code `0`, run:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event req.opsx --req <REQ-id> --change <change-id> --json
```

- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.

## Output Examples

REQ 已纳入 Sprint 且 Change 创建成功时：

```text
下一步：/opsx-apply REQ-0123-import-audio-metadata
待用户决策/处理：
- 无
```

目标 Sprint 不明确时：

```text
下一步：暂无可推进下一步
待用户决策/处理：
- 请选择目标 sprint-xxx。
```

需求需要拆分时：

```text
下一步：暂无可推进下一步
待用户决策/处理：
- 请确认本需求拆分策略。
```

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
