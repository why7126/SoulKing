---
purpose: 治理迭代日志
content: 记录 REQ/BUG review 命令无 flag 默认通过的规范优化
created_at: 2026-08-21 13:46:22
updated_at: 2026-08-21 13:59:26
---

# REQ/BUG Review 默认通过语义

## 迭代目标

降低 `/req-review` 与 `/bug-review` 的常规通过路径输入成本，将无 flag 行为定义为默认 `approve`，只在拒绝、延后或不修复时要求显式 flag。

## 变更摘要

- 新增 OpenSpec Change `simplify-review-default-approval`，补充 `governance-workflow-tooling` delta spec。
- 更新 `/req-review`：无 flag 默认批准；`--reject` 与 `--defer` 作为显式非通过分支。
- 更新 `/bug-review`：无 flag 默认批准；`--reject`、`--defer` 与 `--wont-fix` 作为显式非通过分支。
- 同步命令顺序、需求/BUG 管理规则和各命令最终输出示例，常规通过路径不再推荐 `--approve`。

## 影响范围

- `skills`：评审命令和通用最终输出示例。
- `rules`：需求与 BUG 管理规则。
- `docs`：命令执行顺序、文档索引和规范工程变更历史。
- `OpenSpec`：已归档 Change 与正式治理规格。
- `Sprint`：本次 Change 纳入 `sprint-001` scope。

## 更新文件

- `.agents/skills/req-review/SKILL.md`
- `.agents/skills/bug-review/SKILL.md`
- `.agents/skills/*/SKILL.md` 中的通用下一步示例
- `rules/requirement-management.md`
- `rules/bug-management.md`
- `docs/08-command-execution-order.md`
- `docs/README.md`
- `docs/spec-logs/CHANGELOG.md`
- `openspec/changes/simplify-review-default-approval/`
- `iterations/change/sprint-001/sprint.yaml`
- `iterations/change/sprint-001/sprint.md`
- `iterations/change/sprint-001/acceptance-report.md`
- `data/ai-usage/sprints/sprint-001.json`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-doc-governance.py`：通过。
- `python scripts/validate-doc-prose-hygiene.py <focused-paths>`：通过，输出 4 条启发式 warning，均为既有术语或流程词命中，不阻断。
- `openspec validate simplify-review-default-approval`：通过。
- `openspec status --change simplify-review-default-approval`：通过，4/4 artifacts complete。
- `python scripts/validate-sprint-scope.py sprint-001 --item simplify-review-default-approval`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change simplify-review-default-approval --sprint auto`：通过，解析到 `sprint-001`。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change simplify-review-default-approval --sprint sprint-001 --json`：通过，`usage_mode=actual`，`warning_count=0`。

## 影响评估

- API：无影响。
- DB：无影响。
- 前台 Web：无影响。
- 后台管理端：无影响。
- 桌面封装：无影响。
- 对象存储：无影响。
- Docker：无影响。
- 安全：无权限或密钥处理变化。

## 后续建议

- 后续执行 `/req-review <REQ-full-id>` 或 `/bug-review <BUG-full-id>` 时，默认按通过路径推进。
- 如需拒绝、延后或不修复，显式使用对应非通过 flag。
