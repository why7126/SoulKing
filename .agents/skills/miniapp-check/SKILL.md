---
name: "miniapp-check"
description: "检查微信小程序环境策略、运行入口同步和生产接口可访问性"
---

# miniapp-check

Use this skill when the user asks `/miniapp-check` or wants to verify miniapp environment configuration before preview, trial, review, or release.

## ProjectSoulKing Adapter（MUST）

- 本项目 `project.yaml` 当前 `product_forms.wechat_miniapp.enabled=false`，且默认不存在 `src/miniapp/`。
- 如果 `project.yaml` 未显式启用微信小程序，或 `src/miniapp/` 不存在，MUST stop as BLOCKED，说明当前项目未启用小程序端，并建议先通过 `/req-capture` + OpenSpec Change 引入小程序能力。
- 在阻断状态下不得运行 `scripts/miniapp-env.py` 或 `python -m pytest tests/test_miniapp_static.py`。

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；只读取小程序环境配置、脚本和测试片段。
- 生产 smoke 失败时输出关键状态码和 URL，不输出长响应体。

## Input

- Optional flags: `--smoke` to check production endpoints.

## Must Read

```text
rules/coding.md
rules/testing.md
rules/security.md
rules/agent-context-budget.md
scripts/miniapp-env.py
src/miniapp/utils/env.ts
src/miniapp/utils/env.js
src/miniapp/project.private.config.json
```

## Steps

1. 执行：

```bash
python scripts/miniapp-env.py check --smoke
```

2. 执行静态测试（除非用户只要求快速查看）：

```bash
python -m pytest tests/test_miniapp_static.py
```

3. 报告当前策略、`.ts/.js` 同步状态、`project.private.config.json setting.urlCheck` 是否符合策略、生产接口 smoke 结果、合法域名和手机缓存检查提醒。

## Output

明确给出是否可继续上传体验版；若 blocked，给出最短修复路径。若策略为 `auto` 或 `dev` 且 `urlCheck=true`，优先执行 `python scripts/miniapp-env.py set auto` 或 `set dev` 修复本地开发者工具网络拦截。

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
