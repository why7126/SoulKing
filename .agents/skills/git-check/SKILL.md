---
name: "git-check"
description: "推送前 Git 安全检测 - 检查 staged/tracked 文件中的真实 env、运行时数据、密钥、本机路径、大文件和不应进入 Git 的本地数据"
created_at: 2026-08-10 23:20:00
updated_at: 2026-08-10 23:20:00
---

# git-check

Use this skill when the user asks to run `/git-check`, perform a pre-push Git safety check, or verify that repository changes do not contain secrets, real env files, runtime data, local databases, large artifacts, local absolute paths, or private data.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`。
- 已在同一会话读取过且无变更的规则和 Skill 文件，用摘要承接或摘要复用，不重复全量读取。
- 检索先用 `rg -l` / `rg --files` / `git diff --name-only` 定位，再分段读取必要片段。
- 成功路径只输出扫描摘要、阻断项、warning 和下一步；不得输出完整密钥、Token、连接串、真实 `.env` 行或大段文件内容。

## Command

默认运行：

```bash
python scripts/git-check.py
```

深度复核时可运行：

```bash
python scripts/git-check.py --all
```

## Scope

- 默认扫描 staged + tracked 文件。
- `--all` 扫描全仓当前文件，但不扫描 Git 历史。
- 本地真实 `.env` 只要被 Git ignore 覆盖且未 staged/tracked，不应阻断。

## Guardrails

- 不自动修改 `.gitignore`。
- 不自动 unstage。
- 不删除本地文件。
- 不读取或输出 ignored 且未 staged/tracked 的真实 `.env` 内容。
- 不新增 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/`。

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
