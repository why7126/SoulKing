---
name: "req-explore"
description: "需求探索 - 思考分析已记录需求，默认不写任何文档"
---

# req-explore

Use this skill when the user asks to run the workflow command `req-explore`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

对标 `/opsx-explore`，面向 **需求域**。探讨范围、用户、风险、与现有 REQ 重复、是否子需求。

**Input**：`REQ-xxxx` 或 capture 阶段的一句话（无 ID 则先建议 `/req-capture`）

**默认**：**不生成任何文件、不写代码**。

**可选**：用户明确要求「记录结论」时，才更新 `capture.md#探索结论`；可将 trace `status` 标为 `exploring`。

---

## Stance

- 好奇、可视化（ASCII 依赖/范围图）
- 可读 `capture.md`、类似 REQ、相关 `src/`（只读）
- 不 prescriptive 到单一方案

## 可探讨

- 范围 In/Out、与 REQ-0005 等重复？
- 子需求 vs 独立 REQ
- UI 是否需要 prototype
- 技术风险与 Sprint 容量

## 禁止

- 写 `requirement.md`、六件套、OpenSpec
- 写 `src/`
- 自动更新文件（除非用户明确要求）

## Next

`/req-generate REQ-xxxx` 或继续 explore

## Final Step — AI Usage Post-command Hook (MUST)

Because explore mode normally does not change workflow state, run the hook in dry-run mode before ending:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event req.explore --req <REQ-id> --dry-run --json
```

- If no REQ ID exists yet, omit `--req`.
- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- Do not update REQ/BUG/Change/Sprint status only to create usage data.

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
