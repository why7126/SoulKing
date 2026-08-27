---
purpose: 跨项目 Harness 学习报告
content: 学习 ProjectTilesFST 的 spec-opt 与 spec-study 治理能力并应用到 ProjectSoulKing
created_at: 2026-08-07 12:17:33
updated_at: 2026-08-07 13:04:31
---

# ProjectTilesFST Spec Governance 学习报告

## 学习对象与模式

- 学习对象：`<local-project>/ProjectTilesFST`
- 学习模式：`auto`，聚焦 `spec-opt` 与 `spec-study`
- 学习时间：2026-08-07 12:17:33 Asia/Shanghai

## 学习到的治理能力

- `/spec-study` 采用两阶段流程：先只读学习并输出候选内容，用户确认后再应用到本项目治理资产。
- `/spec-study` 对学习对象强制只读，禁止写入、安装依赖、格式化、迁移、测试修复、提交、清理或重置。
- 学习范围不能只看单一目录，需横向覆盖项目入口、`rules/`、`docs/`、Agent 目录、`scripts/`、部署和 env 示例。
- `/spec-opt` 完成治理资产迭代后需要写入 `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md` 治理日志。
- `/spec-study` 应写入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md` 学习报告；同一次学习应用流程只保留一份正式 study 报告。
- `docs/spec-logs/` 不得包含隐私数据、真实密钥、本机绝对路径、未脱敏日志或学习对象源码。

## 已采纳内容

- 新增 `.agents/skills/spec-study/SKILL.md`，并按 ProjectSoulKing 的 `app/`、`app/static/`、`packaging/` 业务边界重写 Scope 和影响矩阵。
- 更新 `.agents/skills/spec-opt/SKILL.md`，补齐自动 Sprint 编号、治理迭代日志和 `docs/spec-logs/` 输出要求。
- 更新 `AGENTS.md`、`project.yaml`、`rules/directory-structure.md`、`rules/agent-context-budget.md`、`docs/README.md`，把 `/spec-study` 和规范工程日志纳入项目事实源。
- 更新 `scripts/validate-agent-context-budget.py` 和 `scripts/validate-directory-structure.py`，让新增 Skill 和日志目录可被真实校验。
- 本次 apply 聚焦 `agent-context-budget`、`directory-structure`、`deploy-mintlify-release`，补强命令输出契约、完成检查清单、摘要复用、默认搜索排除、deploy/Mintlify/release 事实源边界和公开安全校验。
- 为本次治理应用创建 OpenSpec Change `study-projecttilesfst-governance-hardening` 和 `sprint-001`，使纯治理 Change 也纳入 Sprint scope。

## 未采纳内容

- 未采纳 TilesFST 的 `src/` 业务边界，ProjectSoulKing 当前业务代码仍以 `app/` 和 `app/static/` 为事实源。
- 未采纳小程序、Orval、订单、客户数据等 TilesFST 业务或交付语境；ProjectSoulKing 的小程序命令仅作为兼容入口保留。
- 未同步 TilesFST 的历史 OpenSpec archive、Sprint 目录或业务专属脚本；这些属于源项目状态或业务语境，不适合直接搬入本项目。

## 更新文件清单

- `.agents/skills/spec-study/SKILL.md`：新增跨项目治理学习应用命令。
- `.agents/skills/spec-opt/SKILL.md`：新增治理日志与自动 Sprint 编号规则。
- `AGENTS.md`：补充 `/spec-study` 命令入口。
- `project.yaml`：补充 `governance: [/spec-opt, /spec-study]`。
- `rules/directory-structure.md`：登记 `docs/spec-logs/` 和 `/spec-study`。
- `rules/agent-context-budget.md`：补充 `spec-opt/spec-study` 上下文预算、只读学习、日志和脱敏约束。
- `docs/README.md`：补充规范工程日志索引。
- `scripts/validate-agent-context-budget.py`：把 `spec-study` 纳入命令 Skill 校验。
- `scripts/validate-directory-structure.py`：把 `spec-study`、`docs/spec-logs/`、deploy 内部边界、Mintlify 公开安全边界纳入目录结构校验。
- `scripts/validate-mintlify-site.py`：加强 `.env.*`、构建产物、运行时数据库/日志、大文件和敏感配置片段扫描。
- `rules/release.md`：补充旧版本 usage docs 快照保护、完整页面基线、Mintlify 多版本站点与 `/docs` 部署边界。
- `docs/02-deployment.md`、`deploy/README.md`：补充部署矩阵原则、脚本集中和安全边界。
- `docs/spec-logs/.gitkeep`：保留规范工程日志目录。
- `openspec/changes/study-projecttilesfst-governance-hardening/`：记录本次治理变更事实源。
- `iterations/change/sprint-001/`：承载本次纯治理 Change。

## 影响范围

- API：无接口契约变更。
- 数据库：无 schema 变更。
- 前台 Web：无业务 UI 变更。
- 后台管理端：无业务 UI 变更。
- 桌面封装：无运行时变更。
- 对象存储：无运行时变更。
- Docker Compose：无运行时变更。
- 测试：新增和更新治理校验覆盖。

## 校验结果

- `PYTHONDONTWRITEBYTECODE=1 python scripts/validate-directory-structure.py`：通过。
- `PYTHONDONTWRITEBYTECODE=1 python scripts/validate-mintlify-site.py`：通过。
- 其他治理校验将在本次同步完成后统一运行并在最终回复中汇总；若失败，应先修复治理资产再结束任务。

## 学习对象只读保护

本次对学习对象仅执行只读文件检索、片段读取和 Git 状态查看；未在学习对象路径内写入文件、运行安装、格式化、迁移、清理、提交、重置或构建命令。

## 后续建议

- 后续使用 `/spec-study <学习对象>` 时，先输出候选学习项；只有用户明确确认应用范围后才落盘。
- 若 `/spec-study apply` 或 `/spec-opt` 引入治理行为变化，应配套 active OpenSpec Change，并先纳入 Sprint scope。
