---
purpose: 跨项目治理学习报告
content: 学习并应用 ProjectMoonBox 的命令顺序、Git 安全、Issues 当前态看板、原型 UI 验收和上下文预算治理
created_at: 2026-08-10 23:38:48
updated_at: 2026-08-10 23:38:48
---

# ProjectMoonBox 治理学习应用报告

## 学习对象与模式

- 学习对象：ProjectMoonBox（本地只读项目）
- 学习模式：`auto`
- Focus：`command-execution-order`、`git-check`、`issues-changelog-current-state`、`prototype-ui-acceptance`、`agent-context-budget`
- 执行时间：2026-08-10 23:38:48

## 学习到的治理能力

- 命令执行顺序：先评审、再纳入 Sprint、再创建 Change、再 apply/archive，发布、镜像和产品手册位于交付闭环之后。
- Git 安全检查：推送前扫描 staged/tracked 文件中的真实 env、运行时数据、密钥、连接串、本机路径和大文件。
- Issues 当前态看板：`issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md` 作为人工入口索引，但不替代机器事实源。
- 原型驱动 UI 验收：带 prototype 的 UI Change 必须有 UI Contract、Skeleton、截图、computed style 和 Mock/API 边界。
- Agent 上下文预算：强化日志优先学习、摘要复用、force-proceed follow-up、完整 REQ/BUG 下一步参数和隐私路径校验。

## 已采纳内容

- 采纳 SoulKing 版 `docs/08-command-execution-order.md`，用于统一命令推荐顺序和串行写入边界。
- 采纳 SoulKing 版 `/git-check` 技能与 `scripts/git-check.py`，用于本地 Git 安全门禁。
- 采纳 Issues 当前态看板规则，写入 REQ、BUG 和生命周期规则。
- 采纳 SoulKing 静态 Web 适配版 `docs/standards/prototype-ui-acceptance.md`，并由 `rules/ui-design.md` 引用。
- 采纳上下文预算校验增强，覆盖 git-check、完整 REQ/BUG 参数、隐私路径和 force-proceed follow-up。

## 未采纳内容

- 未采纳 ProjectMoonBox 的 React、Shadcn/UI、MySQL、AI 软件工厂业务语境；原因是 SoulKing 当前技术栈为 FastAPI + SQLite + MinIO + 静态 Web 壳。
- 未采纳 MoonBox 的生产 Mintlify 矩阵细节；原因是 SoulKing 已有独立 release / usage docs / Mintlify 边界。
- 未恢复 `.cursor/`、`.codex/`、`.kiro/`、`.opencode/` 或 `.claude/`；原因是 SoulKing 当前唯一 Agent 入口是 `.agents/skills/`。

## 更新文件清单

- `openspec/changes/study-projectmoonbox-governance-hardening/`：记录本次治理学习应用的 proposal、design、tasks 和 delta spec。
- `iterations/change/sprint-001/sprint.yaml`：将本次纯治理 Change 纳入 Sprint scope。
- `AGENTS.md`：补充 `/git-check`、命令顺序和 prototype UI 规则入口。
- `project.yaml`：补充 git 命令族。
- `.agents/skills/git-check/SKILL.md`：新增推送前 Git 安全检测命令。
- `scripts/git-check.py`：新增 staged/tracked 安全扫描脚本。
- `scripts/validate-agent-context-budget.py`：增强技能门禁和治理文档隐私路径校验。
- `docs/08-command-execution-order.md`：新增命令顺序速查。
- `docs/standards/prototype-ui-acceptance.md`：新增 prototype UI 验收标准。
- `rules/agent-context-budget.md`、`rules/issues-lifecycle.md`、`rules/requirement-management.md`、`rules/bug-management.md`、`rules/ui-design.md`、`rules/directory-structure.md`：同步规则入口和门禁。
- `docs/README.md`、`docs/spec-logs/CHANGELOG.md`：同步文档索引和规范工程历史。

## 影响面

- API：无业务 API 变更。
- 数据库：无 schema 变更。
- 前台 Web：无 `app/static/` 实现变更；仅新增后续 UI Change 的验收规则。
- 后台管理端：无实现变更。
- 桌面封装：无影响。
- 对象存储：无实现变更。
- Docker Compose：无变更。
- 测试：新增治理脚本，需运行脚本自检和现有治理校验。

## 校验命令和结果

- `python scripts/validate-agent-context-budget.py`：通过，36 个命令技能与 49 个技能满足上下文预算、输出契约、Sprint 门禁和隐私路径校验。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/git-check.py`：通过，未发现阻断项或 warning。
- `openspec validate study-projectmoonbox-governance-hardening`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change study-projectmoonbox-governance-hardening --sprint auto`：通过，解析到 `sprint-001`，Updated 2，Errors 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change study-projectmoonbox-governance-hardening --sprint sprint-001 --json`：通过，`usage_mode: actual`，`warning_count: 0`。

## 学习对象只读保护结果

本次仅对 ProjectMoonBox 使用只读扫描、分段读取和 `git status --short` 复核；未执行写入、安装、格式化、测试修复、提交、分支、清理或重置命令。学习对象原本存在未提交改动，本次未改变其状态。

## 后续建议

- 后续可将 Issues 当前态看板刷新接入 Workflow Sync 自动维护。
- 后续可将 prototype UI 证据检查沉淀为 `/opsx-archive` 前置脚本。
