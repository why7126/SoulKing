---
name: "miniapp-env"
description: "切换微信小程序 API 环境策略：dev、prod、auto"
---

# miniapp-env

Use this skill when the user asks `/miniapp-env <dev|prod|auto>` or wants to switch the miniapp API environment.

## ProjectSoulKing Adapter（MUST）

- 本项目 `project.yaml` 当前 `product_forms.wechat_miniapp.enabled=false`，且默认不存在 `src/miniapp/`。
- 如果 `project.yaml` 未显式启用微信小程序，或 `src/miniapp/` 不存在，MUST stop as BLOCKED，说明当前项目未启用小程序端，并建议先通过 `/req-capture` + OpenSpec Change 引入小程序能力。
- 在阻断状态下不得运行 `scripts/miniapp-env.py set|prepare|restore|confirm`，不得创建 `src/miniapp/`。

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；先定位再分段读取，避免全量展开无关目录。
- 只读取小程序环境相关文件、脚本和必要规则；不要默认读取全部 docs、issues、iterations 或 archive。

## Input

- `dev`：所有运行形态使用本地 API：`http://127.0.0.1:8010`，fallback 到 `localhost:8010`、`localhost:8000`。
- `prod`：所有运行形态使用生产 API；ProjectSoulKing 尚未配置生产小程序合法域名。
- `auto`：开发版使用本地，体验版和正式版使用生产。

DevTools URL 校验随策略同步：

- `dev` / `auto` MUST 将 `src/miniapp/project.private.config.json` 的 `setting.urlCheck` 设为 `false`，否则开发版本地 HTTP API 会被微信开发者工具拦截并显示“网络开小差”。
- `prod` MUST 将 `setting.urlCheck` 设为 `true`，用于体验版、提审和正式发布前验证生产合法域名。

## Must Read

```text
rules/coding.md
rules/testing.md
rules/directory-structure.md
rules/agent-context-budget.md
src/miniapp/README.md
scripts/miniapp-env.py
```

## Steps

1. 确认参数为 `dev`、`prod` 或 `auto`；缺失时询问用户目标策略。
2. 执行：

```bash
python scripts/miniapp-env.py set <strategy>
```

3. 执行：

```bash
python -m pytest tests/test_miniapp_static.py
```

4. 输出当前策略、`project.private.config.json setting.urlCheck`、修改文件、测试结果和下一步建议。

## Output

说明是否影响 API、数据库、Web、小程序、管理端；是否需要 Orval；是否需要 Docker Compose 验证；是否补充或更新测试；遵循了哪些 `rules/` 文件。

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
