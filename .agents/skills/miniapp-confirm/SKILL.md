---
name: "miniapp-confirm"
description: "记录小程序体验版或正式版验证确认结论"
---

# miniapp-confirm

Use this skill when the user asks `/miniapp-confirm` or wants to record trial/release verification results for the miniapp.

## ProjectSoulKing Adapter（MUST）

- 本项目 `project.yaml` 当前 `product_forms.wechat_miniapp.enabled=false`，且默认不存在 `src/miniapp/`。
- 如果 `project.yaml` 未显式启用微信小程序，或 `src/miniapp/` 不存在，MUST stop as BLOCKED，说明当前项目未启用小程序端，并建议先通过 `/req-capture` + OpenSpec Change 引入小程序能力。
- 在阻断状态下不得运行 `scripts/miniapp-env.py confirm`，不得写入小程序验收通过结论。

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；只读取小程序环境配置、脚本和相关发布记录片段。
- 不记录敏感信息、微信会话密钥、Cookie、Authorization header、`.env` 内容或真实用户隐私。

## Input

Recommended flags:

```text
--channel trial|release
--version <version>
--result passed|blocked|follow_up
--notes <text>
```

## Steps

1. 确认渠道、版本和验证结果；缺失时询问用户。
2. 执行：

```bash
python scripts/miniapp-env.py confirm --channel <trial|release> --version <version> --result <passed|blocked|follow_up> --notes "<text>"
```

3. 输出可复制到 release、Sprint 验收报告或发布记录的安全摘要。

## Output

报告确认结论、验证范围、剩余风险和下一步 `/miniapp-restore`。

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
