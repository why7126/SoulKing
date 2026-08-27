---
name: "req-generate"
description: "需求生成 - 仅生成 requirement.md（PRD）"
---

# req-generate

Use this skill when the user asks to run the workflow command `req-generate`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

**Input**：`REQ-xxxx`（须存在 `capture.md`）

**Output**：**仅** `requirement.md`；`trace.md` → `status: draft`，`lifecycle.generated`

**禁止**：user-stories、acceptance、prototype、openspec、src

---

## Steps

1. 读 `capture.md`、探索对话上下文、`rules/requirement-management.md`
2. 读 1–2 个同类 REQ 作结构参考（如 `REQ-0005-user-management-list-refine/requirement.md`）
3. 写 `requirement.md` frontmatter：

```yaml
---
requirement_id: REQ-xxxx
title:
terminal: web-admin | web-catalog | miniapp | multi
version: v1
status: draft
owner: product
source: capture.md
priority: P1
parent_requirement:
---
```

4. 正文含：背景、目标用户、范围（含/不含）、功能要求（FR-xxx）、UI 约束、关联需求、状态块
5. 同步 `requirement.md` 与 `trace.md` 的 `status: draft`
6. 追加 trace 变更记录

## 产品数据采集与链路观测门禁

若需求涉及 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测，MUST 读取 `docs/standards/product-data-collection-observability.md`，并在 `requirement.md` 状态块声明 `product_data_collection_observability`、`affected_layers`、`reason` 和 `validation`。

若不适用，MUST 写明为什么不影响 API、DB、请求日志、行为事件、Task Trace、端请求封装、媒体链路或对象存储；不得只写“无”或“不涉及”。

## Next

`/req-complete REQ-xxxx`

---

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event req.generate --req <REQ-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync exits with code `0`, run:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event req.generate --req <REQ-id> --json
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
