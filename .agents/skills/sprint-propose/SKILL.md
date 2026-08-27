---
name: "sprint-propose"
description: "提议并创建新 Sprint 迭代规划（四件套）"
---

# sprint-propose

Use this skill when the user asks to run `/sprint-propose` or create/update a Sprint plan.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- Sprint 范围分析先读取候选 `trace.md` 与摘要，不得全量展开上一 Sprint 四件套、复盘库或所有 active changes。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 不要 `ls -R` 或全量 `cat iterations/** docs/knowledge-base/**`；先列清单，再分段读取。
- 复盘默认只读最近 1 份；只有 open 行动项跨 Sprint 复发或用户要求时读第 2 份。
- `best-practices/` 只读取候选 REQ/BUG/Change 标签命中的文件。
- 已存在 Sprint 时先读 `sprint.yaml` 和 `sprint.md` 的目标/Scope/知识库承接片段。
- 搜索候选项默认排除 `openspec/archive/**` 与 legacy `openspec/changes/archive/**`；编号冲突只看目录名。
- 命令输出优先 `max_output_tokens <= 8000`。

## Input

- `sprint-xxx`：指定 Sprint ID。
- 自然语言目标：由 Agent 推导候选范围和编号。
- Flags：`--req`、`--bug`、`--change`、`--duration 2w`、`--dry-run`。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/document-governance.md
rules/requirement-management.md
rules/bug-management.md
rules/directory-structure.md
rules/iterations-lifecycle.md
.agents/skills/workflow-sync/SKILL.md
docs/knowledge-base/README.md（存在时）
```

按候选范围分段读取：

```text
project.yaml（容量，若存在）
issues/requirements/{plan,review,archive}/<REQ>/trace.md + requirement/acceptance 摘要
issues/bugs/{plan,review,archive}/<BUG>/trace.md + bug/root-cause/acceptance 摘要
openspec/changes/<change>/proposal.md + tasks.md 摘要
iterations/change|archive/<sprint>/sprint.yaml（编号/冲突）
docs/knowledge-base/retrospectives/<latest>-retrospective.md（最近复盘）
docs/knowledge-base/best-practices/<matched>.md（按标签）
```

## Gates

### Sprint Selection Gate（MUST）

选择或创建 Sprint 前 SHOULD 运行：

```bash
python scripts/validate-sprint-selection.py [--sprint <sprint-id>]
```

- 当用户未指定 Sprint ID 且当前没有 `iterations/change/sprint-xxx/` active Sprint 时，MAY 自动创建下一个连续编号 Sprint。
- 当用户未指定 Sprint ID 且当前仅有一个 active Sprint 时，MUST 默认使用该 Sprint 作为当前 Sprint。
- 当用户未指定 Sprint ID 且当前存在两个或以上 active Sprint 时，MUST 阻断命令，并引导用户使用 `/sprint-propose --sprint <sprint-id>` 指定当前 Sprint。
- 用户显式指定尚不存在的 Sprint 时，该 Sprint ID MUST 等于最大规范编号加一；不得跳号创建。
- 如果已存在一个 active Sprint，只有当前 Sprint 容量硬阻断或用户明确拆分范围时，才允许通过 `--sprint <next-sprint>` 创建下一个连续编号 Sprint。
- `<next-sprint>` MUST 通过 `python scripts/validate-sprint-selection.py --sprint <next-sprint>`。
- 如果已存在两个 active Sprint，MUST 禁止创建第三个 active Sprint；用户只能指定其中一个现有 active Sprint。

### Review Gate（MUST）

纳入 Sprint 正式规划前，REQ/BUG status MUST 为 `approved` 或 `in_sprint`。

未评审条目：

- 不得写入 `sprint.yaml` 的 `requirements[]` / `bugs[]`。
- 不得写入 Sprint 目标、Scope、里程碑、工作量合计、release、acceptance 正式范围。
- 不得更新 `trace.md` `iteration`。
- 只能列入 `sprint.md`「延后项（待评审）」并提示 `/req-review` 或 `/bug-review`。

### Readiness Gate

| 类型 | Ready 条件 | Not Ready 处理 |
|---|---|---|
| REQ | `requirement.md`、`acceptance.md`、`trace.md` 齐全且 approved/in_sprint | 延后并建议 `/req-complete` 或 `/req-review` |
| BUG | `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md` 齐全且 approved/in_sprint | 延后并建议 `/bug-complete` 或 `/bug-review` |
| Change | `proposal.md`、`design.md`、`tasks.md` 存在且未 archived | 缺失时提示 `/req-opsx` 或 `/bug-opsx` |

### Capacity Gate

- 优先级：P0 BUG > P0 REQ > P1 > P2。
- 估算：XS=0.5、S=1、M=3、L=5、XL=8、XXL=13 人天。
- add-* 主能力 SHOULD <= 6。
- fix 缓冲 SHOULD >= 30% SP/人天。
- 新建 Sprint 默认使用 `project.yaml` 的 `ai.sprint_capacity.capacity_person_days` 作为 `capacity_person_days`；若未配置，MUST 要求用户显式确认容量。
- 必须在生成正式四件套或更新 REQ/BUG/Change trace 前计算：
  `capacity_usage = estimated_person_days / capacity_person_days`。
- 若容量或估算缺失导致无法计算，MUST 先补齐输入；不得默认通过。
- `estimated_person_days > capacity_person_days * 1.2` 时 MUST 硬阻断正式规划：
  - 不得生成 `iterations/change/<sprint>/` 四件套。
  - 不得写入当前 Sprint 的 `sprint.yaml` 正式 scope。
  - 不得更新 `trace.md` 的 `iteration` 或 Change trace。
  - 输出硬提示：必须拆分 Sprint、移出低优先级项、替换范围，或使用 `/sprint-propose --sprint <next-sprint>` 创建下一个连续编号 Sprint 后重新规划。
  - `<next-sprint>` MUST 通过 `scripts/validate-sprint-selection.py --sprint <next-sprint>`，不得跳号。
- `capacity_person_days < estimated_person_days <= capacity_person_days * 1.2` 时 MAY 继续，但 MUST 写入容量风险、fix 缓冲影响和延后项建议。
- `estimated_person_days <= capacity_person_days` 时按既有 Review Gate、Readiness Gate 和 Capacity Gate 继续。

### 产品数据采集与链路观测门禁（MUST）

纳入 REQ、BUG 或 Change 时，若范围涉及 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测，MUST 读取 `docs/standards/product-data-collection-observability.md` 或确认相关 REQ/Change 已引用，并在 Sprint 输出摘要中提示 `product_data_collection_observability` 状态、`affected_layers` 适用层级、N/A 原因、`reason`、`validation` 验证摘要或缺失项。

## Knowledge Intake

- 读取最近 Sprint 复盘，提取 open 行动项并写入 §知识库承接。
- 按范围标签选择 best-practices：`admin-list`、`admin-form`、`admin-modal`、`media-upload`。
- `sprint.md` 必须包含 §横切预防清单，列出适用 best-practices 与验收 gate 摘要。

## Artifacts（非 `--dry-run` MUST）

目录：`iterations/change/sprint-xxx/`

```text
sprint.yaml
sprint.md
release-note.md
acceptance-report.md
```

`sprint.yaml` MUST 包含：

```yaml
sprint_id: sprint-xxx
status: planning
lifecycle_stage: change
start_date: YYYY-MM-DD HH:mm:ss
end_date: YYYY-MM-DD HH:mm:ss
capacity: { developers: <int>, testers: <int> }
capacity_person_days: <number>
requirements: []
bugs: []
changes: []
estimated_story_points: <number>
estimated_person_days: <number>
capacity_usage: <number>
fix_buffer_person_days: <number>
fix_buffer_ratio: <number>
capacity_gate:
  capacity_person_days: <number>
  estimated_person_days: <number>
  capacity_usage: <number>
  result: pass|pass_with_risk|blocked
  note: <容量门禁摘要、fix 缓冲影响和延后建议>
```

`sprint.md` MUST 包含：目标、Scope、工作量、fix 缓冲、里程碑、风险、知识库承接、横切预防清单、依赖 ASCII 树、发布计划、关联文档。

Markdown frontmatter MUST 含 `created_at`、`updated_at`；更新只改 `updated_at`。

## Trace Updates

对纳入的 REQ/BUG/Change 更新：

```text
trace.md iteration: sprint-xxx
openspec/changes/<change>/trace.md（若存在）
```

## Existing Sprint Scope Update（MUST）

当目标 `iterations/change|archive/<sprint>/sprint.yaml` 已存在，且本命令是在已有 Sprint 中追加或修正 REQ/BUG/Change 正式范围时，MUST 先使用确定性脚本更新机器事实源，不得只手工编辑 `sprint.md`、Issue trace 或 Markdown Scope 表：

```bash
python scripts/add-sprint-scope-item.py \
  --sprint <sprint-id> \
  [--req <REQ-id> | --bug <BUG-id>] \
  [--change <change-id>] \
  --size <XS|S|M|L|XL|XXL> \
  --story-points <number> \
  --person-days <number> \
  --rationale "<估算与影响说明>"
```

- 脚本成功后再运行 Workflow Sync 派生刷新 `sprint.md`、`release-note.md`、`acceptance-report.md`、Issue trace 和 Change trace。
- 多个范围项追加到同一个 Sprint 时，MUST 严格串行运行 `scripts/add-sprint-scope-item.py`；不得使用并行工具同时写同一个 `sprint.yaml`。脚本虽然带文件锁，但命令编排仍必须以最新写入后的 YAML 作为下一项输入，避免覆盖、重复键或坏 UTF-8。
- `sprint.md` `## 1. 目标` 的 Sprint 目标编号列表 MUST 同步包含写入或修正的 REQ/BUG/必要纯 Change；对应要点段落 SHOULD 补齐或更新。
- `sprint.md` `## 2. Scope` 主表 MUST 保持六列：`类型 | 编号 | 标题 | 状态 | 估算 | 说明`。不得改成 `范围项 | 状态 | 估算` 窄表；需要降低预览宽度时，只能缩短 `说明` 文案或把细节放入 workflow-sync 分组表。
- 若新增项带有 Change，结束前 MUST 运行 `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run`，并确认输出解析到目标 Sprint，不得报告 `not in sprint scope`。
- 若 dry-run 仍报告 `not in sprint scope`，MUST 停止并修复 `sprint.yaml` 机器源；不得以 `sprint.md` Scope 表或人工摘要已出现该项作为完成依据。

## Output

报告 Sprint ID、状态、纳入 REQ/BUG/Change 数量、估算、知识库承接、容量门禁、四件套路径、下一步。

## Final Step — Workflow Sync（MUST）

Run:

```bash
python scripts/sync-workflow-status.py --event sprint.propose --sprint <sprint-id>
```

- Exit code MUST be `0`。
- Print summary Workflow Sync Report；use `--output detail` only for debugging。
- Do not hand-edit workflow-sync marker blocks。

Then validate the user-readable Sprint Scope view:

```bash
python scripts/validate-sprint-scope.py <sprint-id> \
  [--item <REQ-id>] [--item <BUG-id>] [--item <change-id>]
```

- Exit code MUST be `0` before finishing `/sprint-propose`.
- Pass every REQ/BUG/Change newly added or updated by this run.
- This check is required because `sprint.yaml` is the machine source, while `sprint.md` `## 1. 目标` and `## 2. Scope` are product-facing planning sources; all three MUST contain the same formal scope.

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync exits with code `0`, run:

```bash
python scripts/extract-ai-usage.py \
  --post-command-hook \
  --workflow-event sprint.propose \
  --sprint <sprint-id> \
  [--req <REQ-id>] \
  [--bug <BUG-id>] \
  [--change <change-id>] \
  --json
```

- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- Pass every REQ/BUG/Change newly added or updated by this `/sprint-propose` run so the hook can attribute the correct command run and auto-discover the local session when `--session-jsonl` is not available.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.

## Output Examples

成功纳入已评审 REQ 时：

```text
下一步：/req-opsx REQ-0123-import-audio-metadata
待用户决策/处理：
- 无
```

成功纳入已评审 BUG 时：

```text
下一步：/bug-opsx BUG-0144-audio-upload-thumbnail-regression
待用户决策/处理：
- 无
```

Sprint 编号或范围选择被阻塞时：

```text
下一步：暂无可推进下一步
待用户决策/处理：
- 请指定当前 active Sprint 或调整本次 Sprint 范围。
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
