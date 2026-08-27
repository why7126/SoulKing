---
name: "capture"
description: "智能收集 - 自动区分需求与缺陷，按需拆分并分别走 req-capture / bug-capture 落盘"
---

# capture

Use this skill when the user asks to run the workflow command `capture`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

**Input**：用户不确定是需求还是 BUG 时的原始描述；可含混合多条。可选：`--priority`、`--severity`、`--parent REQ-xxxx`

**Output**：分类分析表 + 各 REQ/BUG 的 capture.md + trace.md + registry 更新

**禁止**：`requirement.md`、`bug.md`、`src/`、`openspec/`

**定位**：类型已知时用 `/req-capture` 或 `/bug-capture`；本命令用于类型未决或混合输入。

---

## Steps

1. 读 `rules/requirement-management.md`、`rules/bug-management.md`、两个 `_registry.yaml`
2. **解析 → 分类（REQ/BUG）→ 拆分**（见 `.agents/skills/capture/SKILL.md`）
3. 落盘：REQ 遵循 req-capture 模板与规则；BUG 遵循 bug-capture 模板与规则；frontmatter 加 `captured_via: capture` 与 `classification_rationale`
4. 输出分类分析表 + Capture 摘要

---

## 分类要点

- 已有能力/规范下的偏差 → **BUG**
- 尚未交付的新能力/流程 → **REQ**
- 混合输入 → 拆条目后分别归类
- 新功能 PRD 未达标 → BUG + `related_requirement`
- 边界不清 → 分类表标注待澄清，capture 写待澄清项

拆分分别套用 `/req-capture` Multi-REQ 与 `/bug-capture` Multi-BUG 规则。

---

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md`.对每条创建的 REQ / BUG：

```bash
for req in REQ-xxxx-slug ...; do
  python scripts/sync-workflow-status.py --event req.capture --req "$req" --sprint auto || exit 1
done
for bug in BUG-xxxx-slug ...; do
  python scripts/sync-workflow-status.py --event bug.capture --bug "$bug" --sprint auto || exit 1
done
```

- Exit code **MUST** be `0`
- Print summary **Workflow Sync Report**（注明 REQ N 条 + BUG M 条）；use `--output detail` only for debugging
- Do **not** hand-edit `sprint.md` Scope marker blocks

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync exits with code `0`, run the unified AI usage hook for **each created REQ / BUG**:

```bash
for req in REQ-xxxx-slug ...; do
  python scripts/extract-ai-usage.py --post-command-hook --workflow-event req.capture --req "$req" --json || exit 1
done
for bug in BUG-xxxx-slug ...; do
  python scripts/extract-ai-usage.py --post-command-hook --workflow-event bug.capture --bug "$bug" --json || exit 1
done
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
