---
name: "build-api-standard"
description: "建立 API Governance（统一响应 / 错误码 / OpenAPI / Orval）"
---

# build-api-standard

Use this skill when the user asks to run the workflow command `build-api-standard`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

将 `rules/api.md` 落地为可执行 API 治理：文档、Schema、校验脚本与 FastAPI 分层约定。

**关联 REQ**：`REQ-0000-build-api-standard`（`change_id: build-api-standard`，已归档见 `openspec/specs/api-governance/`）

**Input**：`--verify` 仅校验

---

## 必须读取

```text
AGENTS.md
rules/api.md
rules/security.md
rules/testing.md
rules/coding.md
openspec/specs/api-governance/spec.md
app/**
app/static/**
docs/03-api-index.md
```

---

## 与 req / opsx 关系

| 场景 | 做法 |
|------|------|
| 新业务 API | 对应业务 REQ 的 `/req-opsx` → `add-*` |
| 治理规范变更 | 新 REQ + `/req-opsx`（MODIFIED `api-governance`） |
| 接口实现后 | **MUST** 更新 OpenAPI + `scripts/generate-openapi-client.sh` |

---

## Step 1 — 治理文档

核对/更新：

```text
docs/standards/api-governance.md
docs/standards/error-codes.md
docs/standards/openapi-rules.md
docs/standards/authentication.md
docs/standards/file-upload.md
docs/03-api-index.md
```

---

## Step 2 — 统一结构

```text
app/schemas.py                      # response / request schemas
app/main.py / app/auth_routes.py    # FastAPI routes
app/auth.py                         # auth helpers when auth is affected
```

统一响应：`{ code, message, data }`；分页 `page` / `page_size` / `items` / `total`。

---

## Step 3 — OpenAPI First

- 路由须 `response_model`、`summary`、`tags`
- 以 FastAPI `/openapi.json` 为契约来源
- 本项目未启用 Orval；前端调用位于 `app/static/*.js`

---

## Step 4 — 测试与校验

```text
tests/integration/api/              # 集成测试
scripts/validate-api-standard.py
```

每接口：成功、失败、权限、边界。

---

## Step 5 — OpenSpec

已归档 **勿重建** `build-api-standard`。新治理需求走 `/req-opsx`。

---

## 验收

```text
□ validate-api-standard.py pass
□ FastAPI OpenAPI 可生成
□ error_codes 与 rules/api.md 一致
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
