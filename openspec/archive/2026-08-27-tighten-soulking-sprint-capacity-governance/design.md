---
purpose: OpenSpec Change design
content: Sprint 容量门禁应用设计
created_at: 2026-08-27 08:54:38
updated_at: 2026-08-27 08:54:38
---

# 设计

## 1. 容量模型

Sprint 容量使用 `capacity_person_days` 作为计划容量基线，正式范围估算使用 `estimated_person_days` 汇总。

```text
capacity_usage = estimated_person_days / capacity_person_days
fix_buffer_person_days = max(capacity_person_days - estimated_person_days, 0)
fix_buffer_ratio = fix_buffer_person_days / capacity_person_days
```

容量门禁结果分为三类：

- `pass`：`estimated_person_days <= capacity_person_days`。
- `pass_with_risk`：`capacity_person_days < estimated_person_days <= capacity_person_days * 1.2`。
- `blocked`：`estimated_person_days > capacity_person_days * 1.2`。

## 2. 写入边界

详细容量规则归属：

- `rules/iterations-lifecycle.md`：Sprint 生命周期和容量门禁事实源。
- `.agents/skills/sprint-propose/SKILL.md`：命令执行时的门禁步骤、字段模板和输出要求。
- `openspec/specs/governance-workflow-tooling/spec.md`：归档后的能力约束。
- `scripts/add-sprint-scope-item.py`：已有 Sprint 追加范围时的机器事实源刷新。

入口文件只保留摘要，不复制完整规则正文。

## 3. 超载处理

当候选范围超过 120%：

- 不得生成新的正式 Sprint 四件套。
- 不得更新 REQ、BUG 或 Change trace 的 `iteration`。
- 不得把范围写入当前 Sprint 的 `sprint.yaml`。
- 必须提示拆分 Sprint、移出低优先级项或替换范围。
- 如要创建下一个 Sprint，必须通过 `python scripts/validate-sprint-selection.py --sprint <next-sprint>`，且新 Sprint 必须是最大规范编号加一。

## 4. 当前项目适配

SoulKing 当前采用 `project.yaml` 的 `ai.sprint_capacity.capacity_person_days = 30` 作为新建 Sprint 默认容量基线。具体 Sprint 仍可在 `sprint.yaml` 中记录实际容量；若未来团队规模变化，应先调整 `project.yaml`，再由新 Sprint 继承，历史 Sprint 不反向改写。
