---
created_at: 2026-08-21 00:00:00
updated_at: 2026-08-21 00:00:00
---

# 设计

## 方案

采用“规则补强 + 校验脚本 + Change 追踪 + 学习报告”的轻量落地方式：

- 文档治理：更新 `rules/document-governance.md` 和 `docs/README.md`，把 deepseek-harness 的文档层级、一事实一归属、决策记录和文档杂质检查改写为 SoulKing 的治理规则。
- 验证治理：更新 `rules/testing.md` 和 `docs/standards/testing-governance.md`，要求按 API、DB、UI、部署、脚本、文档等影响面选择最小相关验证。
- BUG 复盘：更新 `rules/bug-management.md`，把系统性、隐蔽、高复现成本缺陷导向 `docs/knowledge-base/incidents/`。
- 脚本门禁：新增 `scripts/validate-doc-governance.py`，只检查治理文档结构、隐私路径、脚手架残留和 AGENTS 字数预算，不修改文件。
- 学习报告：生成一份 `docs/spec-logs/YYYYMMDDhhmmss-study-deepseek-harness-governance.md` 并更新 `docs/spec-logs/CHANGELOG.md`。

## 项目化差异

deepseek-harness 的 Agent Notes、双语配对、包 invariant、Cordis 插件和 TypeScript 发布矩阵不适合直接迁移。SoulKing 保持单一 `.agents/skills/` 入口，把决策记录收敛到 active Change、`docs/spec-logs/` 和必要的 `docs/knowledge-base/`，避免新增平行事实源。

## 校验策略

完成后运行：

- `python scripts/validate-doc-governance.py`
- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate study-deepseek-harness-governance-hardening`
- `python scripts/sync-workflow-status.py --event opsx.apply --change study-deepseek-harness-governance-hardening --sprint auto`
