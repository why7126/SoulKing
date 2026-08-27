---
name: "miniapp-restore"
description: "发布后恢复微信小程序默认环境策略"
---

# miniapp-restore

Use this skill when the user asks `/miniapp-restore` or wants to restore the miniapp environment after trial/release verification.

## ProjectSoulKing Adapter（MUST）

- 本项目 `project.yaml` 当前 `product_forms.wechat_miniapp.enabled=false`，且默认不存在 `src/miniapp/`。
- 如果 `project.yaml` 未显式启用微信小程序，或 `src/miniapp/` 不存在，MUST stop as BLOCKED，说明当前项目未启用小程序端，并建议先通过 `/req-capture` + OpenSpec Change 引入小程序能力。
- 在阻断状态下不得运行 `scripts/miniapp-env.py restore`。

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；只读取小程序环境配置、脚本和静态测试。

## Input

- Optional `--strategy dev|prod|auto`；默认恢复为 `auto`。
- 恢复为 `auto` 或 `dev` 时 MUST 同步关闭 `src/miniapp/project.private.config.json` 的 `setting.urlCheck`，避免开发版本地 HTTP API 被微信开发者工具拦截。

## Steps

1. 执行：

```bash
python scripts/miniapp-env.py restore --strategy auto
```

2. 执行：

```bash
python -m pytest tests/test_miniapp_static.py
```

3. 输出恢复后的策略摘要、`project.private.config.json setting.urlCheck` 和测试结果。

## Output

说明恢复后的策略、修改文件、测试结果、开发者工具是否需要重新编译，以及是否仍需要人工上传小程序。

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
