---
name: "miniapp-prepare"
description: "小程序发布前准备：切生产、静态测试、生产接口 smoke、输出上传体验版清单"
---

# miniapp-prepare

Use this skill when the user asks `/miniapp-prepare` or wants to prepare the WeChat miniapp for trial/review/release.

## ProjectSoulKing Adapter（MUST）

- 本项目 `project.yaml` 当前 `product_forms.wechat_miniapp.enabled=false`，且默认不存在 `src/miniapp/`。
- 如果 `project.yaml` 未显式启用微信小程序，或 `src/miniapp/` 不存在，MUST stop as BLOCKED，说明当前项目未启用小程序端，并建议先通过 `/req-capture` + OpenSpec Change 引入小程序能力。
- 在阻断状态下不得运行 `scripts/miniapp-env.py prepare`，不得修改发布或验收文档为小程序已通过。

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；只读取小程序环境配置、生产发布相关规则和脚本。
- 测试和 curl 输出使用摘要；失败时只展开关键错误。

## Must Read

```text
rules/coding.md
rules/testing.md
rules/security.md
rules/directory-structure.md
rules/agent-context-budget.md
src/miniapp/README.md
scripts/miniapp-env.py
```

## Gates

Prepare MUST be blocked unless:

- 小程序策略成功切到 `prod`。
- `src/miniapp/project.private.config.json` 的 `setting.urlCheck` 已切到 `true`。
- `python -m pytest tests/test_miniapp_static.py` 通过。
- 生产小程序 smoke URL 必须来自 ProjectSoulKing 的小程序 OpenSpec；当前不适用。

## Steps

1. 执行：

```bash
python scripts/miniapp-env.py prepare
```

2. 如 sandbox 阻止 uv 缓存或外网 smoke，按审批规则重跑必要命令。
3. 输出微信开发者工具上传、公众平台设为体验版、手机删除旧体验版入口、重新扫码最新体验版二维码的 checklist。

## Output

报告门禁结果、当前策略、`urlCheck=true` 状态、测试命令、生产接口 smoke、人工 checklist、下一步 `/miniapp-confirm` 或 `/miniapp-restore`。

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
