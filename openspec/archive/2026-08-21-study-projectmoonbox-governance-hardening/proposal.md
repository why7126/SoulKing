---
created_at: 2026-08-10 23:20:00
updated_at: 2026-08-10 23:20:00
---

# 学习 ProjectMoonBox 治理加固

## 背景

用户确认将 ProjectMoonBox 中适合 ProjectSoulKing 的命令顺序、Git 安全检查、REQ/BUG 当前态看板、原型驱动 UI 验收和 Agent 上下文预算经验应用到本项目。

ProjectSoulKing 已有 `.agents/skills/`、OpenSpec、Sprint、spec logs 和基础校验脚本，但缺少推送前 Git 安全门禁、统一命令执行顺序文档、带 prototype UI 的证据化验收标准，以及对 REQ/BUG 当前态索引和技能输出契约的更严格自动校验。

## 变更目标

- 新增 SoulKing 版命令执行顺序速查，统一 REQ/BUG、Sprint、OpenSpec、发布、镜像和产品手册链路。
- 新增 `/git-check` 技能和安全扫描脚本，防止真实 env、运行时数据、密钥、本机路径、大文件和私有数据进入 Git。
- 强化 `issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md` 作为当前态看板索引的规则边界。
- 新增原型驱动 UI 验收标准，并让 `rules/ui-design.md` 引用它。
- 强化 `rules/agent-context-budget.md` 与 `scripts/validate-agent-context-budget.py`，让摘要复用、force-proceed follow-up、完整 REQ/BUG 参数和 Sprint 门禁更可校验。

## 非目标

- 不修改 `app/`、`app/static/`、`packaging/` 下业务运行时代码。
- 不同步 ProjectMoonBox 的 React、Shadcn/UI、MySQL、Mintlify 生产矩阵或 AI 软件工厂业务语境。
- 不修改 ProjectMoonBox 中任何文件、目录、依赖、缓存、Git 状态或运行时数据。

## 风险

- 新增 Git 安全检查后，当前工作区已有的历史运行时数据或私有路径可能被更早暴露为阻断项。
- UI 验收标准会提高后续带 prototype Change 的证据要求，需要在 apply/archive 时补齐截图和 computed style 记录。
