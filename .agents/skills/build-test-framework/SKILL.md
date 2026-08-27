---
name: "build-test-framework"
description: "建立 Testing Governance（pytest / vitest / E2E / CI / 映射）"
---

# build-test-framework

Use this skill when the user asks to run the workflow command `build-test-framework`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

将 `rules/testing.md` 落地为测试目录、基线配置、覆盖率规则与 `validate-test-framework.py`。

**关联 REQ**：`REQ-0000-build-test-standard`（`change_id: build-test-framework`，已归档见 `openspec/specs/testing/`）

**Input**：`--verify` 仅校验

---

## 必须读取

```text
AGENTS.md
rules/testing.md
rules/coding.md
rules/api.md
openspec/specs/testing/spec.md
openspec/testing-mapping.md
tests/
package.json
```

---

## 与 req / opsx 关系

```text
REQ acceptance.md  →  pytest / vitest / e2e
/req-opsx tasks.md   →  MUST 含测试任务
/opsx-apply          →  新增代码必须新增测试
/sprint-apply        →  跑 change 内测试任务
```

BUG 修复：`/bug-opsx` tasks **MUST** 含回归测试。

---

## Step 1 — 治理文档

```text
docs/standards/testing-governance.md
docs/standards/unit-test-standard.md
docs/standards/frontend-test-standard.md
docs/standards/test-coverage.md
openspec/testing-mapping.md
```

金字塔：Unit 70% / Integration 20% / E2E 10%。

---

## Step 2 — 目录与基线

```text
tests/unit/                 # pytest
tests/integration/api/      # FastAPI/TestClient
tests/e2e/                  # Playwright / npm run test:e2e（可选）
tests/fixtures/
.coveragerc
.github/workflows/test.yml
```

`conftest.py`：TestClient、SQLite、MinIO fixture。

---

## Step 3 — 映射

`openspec/testing-mapping.md` 维护：

```yaml
REQ-xxxx:
  acceptance: [AC-001, …]
  tests: [test_…]
```

每个 **approved** REQ 在 `req-complete` 时应有关联测试计划（`test-plan.md` 或 acceptance 内）。

---

## Step 4 — 校验

```bash
python scripts/validate-test-framework.py
python -m pytest
npm run test:e2e
```

---

## Step 5 — OpenSpec

已归档 **勿重建** `build-test-framework`。测试规范变更走新 REQ + `/req-opsx`。

---

## 验收

```text
□ validate-test-framework.py pass
□ CI workflow 存在
□ testing-mapping 含 REQ-0000 三项
□ Backend coverage 目标文档化（≥80%）
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
