---
created_at: 2026-08-10 23:20:00
updated_at: 2026-08-10 23:20:00
---

# 设计

## 方案

采用“文档规则 + Agent 技能 + 校验脚本 + 学习报告”四层同步：

- 文档规则：更新 `AGENTS.md`、`rules/agent-context-budget.md`、`rules/directory-structure.md`、`rules/issues-lifecycle.md`、`rules/requirement-management.md`、`rules/bug-management.md`、`rules/ui-design.md`，新增 `docs/08-command-execution-order.md` 和 `docs/standards/prototype-ui-acceptance.md`。
- Agent 技能：新增 `.agents/skills/git-check/SKILL.md`，并把 `/git-check` 纳入项目技能入口。
- 校验脚本：新增 `scripts/git-check.py`，强化 `scripts/validate-agent-context-budget.py` 对 git-check、完整 REQ/BUG 参数、隐私路径和 follow-up 规则的检查。
- 学习报告：生成一份 `docs/spec-logs/YYYYMMDDhhmmss-study-projectmoonbox-governance.md`，记录采纳、未采纳、影响面和验证结果。

## 项目化差异

ProjectMoonBox 的前端、部署和业务域与 SoulKing 不同，本次只迁移治理模式：

- SoulKing 保持 `app/`、`app/static/`、`packaging/` 业务边界。
- UI 验收围绕静态 HTML/CSS/JavaScript、`ui-design.md`、`studio.css` 和 `admin-studio.css`。
- Git 安全扫描只做本地仓库文件检查，不自动修改 `.gitignore`、不删除文件、不读取 ignored 真实 env 内容。
- REQ/BUG 当前态看板仍只作为人工入口，机器事实源继续是 `_registry.yaml`、单条 `trace.md`、Sprint 四件套和 OpenSpec Change。

## 校验策略

完成后运行：

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `python scripts/git-check.py`
- `openspec validate study-projectmoonbox-governance-hardening`
- `python scripts/sync-workflow-status.py --event opsx.apply --change study-projectmoonbox-governance-hardening --sprint auto`
