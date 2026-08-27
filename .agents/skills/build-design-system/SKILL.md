---
name: "build-design-system"
description: "基于 rules/ui-design.md 建设可执行 Design System（Token / 组件 / 校验）"
---

# build-design-system

Use this skill when the user asks to run the workflow command `build-design-system`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

将 `rules/ui-design.md` 落地为 Token、组件、模板、预览页与 `validate-design-system.py`。

**关联 REQ**：`REQ-0000-build-design-system`（`change_id: build-design-system`，已归档见 `openspec/specs/design-system/`）

**Input**：`--verify` 仅校验；默认实现/补全缺失资产

---

## 必须读取

```text
AGENTS.md
rules/ui-design.md
rules/directory-structure.md
rules/coding.md
rules/testing.md
rules/requirement-management.md
ui-design.md
app/static/*.css
openspec/specs/design-system/spec.md
```

---

## 与 req / opsx 关系

| 场景 | 做法 |
|------|------|
| 绿场首次建设 | `/req-capture` … `/req-opsx` → `add-design-system` 或 `build-design-system` |
| 已归档（本项目） | 直接按本命令补代码；**规范变更**须新 REQ + `/req-opsx` |
| 实现 | `/opsx-apply`（若有活跃 change） |

**禁止**：手写 `openspec/changes/` 无 `.openspec.yaml`；业务页硬编码 Hex。

---

## Step 1 — 目录与 spec

确保存在：

```text
ui-design.md
rules/ui-design.md
app/static/studio.css
app/static/admin-studio.css
app/static/*.html
scripts/validate-design-system.py
```

`design-system/spec.md` 可选；上游以 `rules/ui-design.md` 为准。

---

## Step 2 — Tokens 与 CSS

- 更新 `ui-design.md` 与 `rules/ui-design.md`
- 颜色、间距、层级 → `app/static/studio.css` 与 `app/static/admin-studio.css` CSS variables
- 本项目未启用 Tailwind / shadcn；不得引入前端框架，除非有独立 OpenSpec Change

---

## Step 3 — 组件与模板

按 AGENTS.md Design System 应用规范优先级：

```text
ui-design.md → rules/ui-design.md → app/static/*.css → app/static/*.html / *.js
```

禁止在 `features/` 重复实现 DS 组件。

---

## Step 4 — 预览与校验

- 前台与后台静态页面可展示对应 Token 与组件
- 运行 `python scripts/validate-design-system.py`

---

## Step 5 — OpenSpec（仅当需要新 change）

**不得**重复创建已归档的 `build-design-system`。若需增量能力：

```text
/req-capture → … → /req-review → /req-opsx REQ-xxxx
```

delta spec **MODIFIED** 标题须与 `openspec/specs/design-system/spec.md` 一致。

---

## 验收

```text
□ Token / globals / tailwind 一致
□ 无裸 Hex（校验脚本 pass）
□ DesignSystemPage 可访问
□ REQ-0000 trace 含 change_id: build-design-system
```

## 参考

- `issues/requirements/archive/REQ-0000-build-design-system/`
- `openspec/archive/2026-06-13-add-design-system/`（如存在）

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
