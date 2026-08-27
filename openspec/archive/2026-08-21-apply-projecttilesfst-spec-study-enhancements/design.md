---
created_at: 2026-08-21 08:57:03
updated_at: 2026-08-21 08:57:03
---

# 设计

## 方案

采用“技能规则 + 文档标准 + 校验脚本 + spec-log 报告”四层同步：

- 技能规则：更新 `.agents/skills/spec-study/SKILL.md`，固化日志优先学习、漂移复核、事实唯一归属和学习报告字段。
- 文档标准：更新 `rules/document-governance.md`、`docs/08-command-execution-order.md`、`docs/README.md`、`AGENTS.md`，新增 `docs/standards/document-prose-hygiene.md`。
- 校验脚本：新增 `scripts/validate-doc-prose-hygiene.py`，对长期 Markdown 提供 warning 级启发式扫描。
- 学习报告：生成 `docs/spec-logs/20260821085703-study-projecttilesfst-spec-study.md`，记录采纳、未采纳、取舍、影响和验证。

## 项目化差异

ProjectSoulKing 继续保持 `app/`、`app/static/`、SQLite、MinIO、`.agents/skills/` 和 `docs/spec-logs/` 的现有边界。本次只迁移 ProjectTilesFST 的治理方法，不迁移其业务结构、前端栈、部署矩阵或小程序语境。

## 校验策略

完成后运行：

- `python scripts/validate-doc-prose-hygiene.py <focused-paths> --json`
- `python -m py_compile scripts/validate-doc-prose-hygiene.py`
- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate apply-projecttilesfst-spec-study-enhancements`
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-projecttilesfst-spec-study-enhancements`
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-projecttilesfst-spec-study-enhancements --sprint auto`
