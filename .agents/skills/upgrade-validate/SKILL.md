---
name: "upgrade-validate"
description: "校验版本部署升级与回滚计划"
created_at: 2026-08-21 22:50:52
updated_at: 2026-08-21 22:50:52
---

# upgrade-validate

Use this skill when the user asks `/upgrade-validate --plan <path>` or wants to validate a generated upgrade / rollback plan.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接；只读取指定 plan 和必要的目标 release/image 证据。
- 校验成功默认输出摘要；失败时只展开 blocker/warning 和修复建议。
- 不输出真实 `.env`、密钥、数据库文件路径、连接串、Cookie、Authorization header、本机绝对路径或真实用户数据。

## Must Read

```text
AGENTS.md
rules/release.md
rules/environment.md
rules/database.md
rules/security.md
rules/object-storage.md
<plan path>
```

## Command

```bash
python scripts/validate-release-upgrade.py validate-plan --plan <path>
```

## Boundaries

- MUST NOT 自动执行生产升级。
- MUST NOT 自动修改真实 env。
- MUST NOT 自动执行 SQLite restore、写入型 migration 或对象存储维护任务。

## Output

报告 plan path、from version、to version、support level、blocker/warning 数、校验结果、下一步和待用户决策/处理。

当 `support_level=cross-version-upgrade-requires-manual-review` 时，必须提醒人工复核中间版本 release 事实、env diff、SQLite 备份/恢复、MinIO 对象存储影响和升级/回滚 smoke 证据。

## Output Examples

计划校验通过但等待实施确认时：

```text
下一步：暂无可推进下一步
待用户决策/处理：
- 请确认是否按已校验计划执行生产升级。
```

跨版本事实不足时：

```text
下一步：暂无可推进下一步
待用户决策/处理：
- 请复核中间版本 release 事实。
```

需要生产实施确认时：

```text
下一步：暂无可推进下一步
待用户决策/处理：
- 请完成生产实施确认。
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
