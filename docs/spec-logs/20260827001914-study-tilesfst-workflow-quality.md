---
purpose: 跨项目治理学习报告
content: 记录应用 TilesFST 工作流质量治理学习项 T1-T4 与 sprint.md 治理项 SPM1-SPM4 的采纳内容、影响范围和验证结果
created_at: 2026-08-27 00:19:14
updated_at: 2026-08-27 01:10:11
---

# TilesFST 工作流质量治理学习报告

## 学习对象

- 学习对象：`<Projects>/ProjectTilesFST/ProjectTilesFST`
- 学习模式：`auto`，应用项：`T1,T2,T3,T4`、`SPM1,SPM2,SPM3,SPM4`
- 执行时间：`2026-08-27 00:19:14`、`2026-08-27 01:10:11`，时区：`Asia/Shanghai`

## 学习到的治理能力

- 命令最终输出契约应使用真实结果，避免尖括号占位模板、通用 BUG 示例和规范语气进入最终回复。
- `/sprint-propose` 需要 active Sprint 数量、连续编号和第三个 active Sprint 阻断门禁。
- `/bug-review` 默认 approve 前应要求 `root_cause_status: confirmed`，并校验 confirmed 根因的可定位证据链。
- AI Usage Sprint 复盘矩阵需要区分未观测 workflow 与真实 `0`，用户可见矩阵用 `-` 表示未采集或未归因。
- `sprint.md` 应作为产品可读规划源接受校验：`## 1. 目标` 编号列表、`## 2. Scope` 六列主表和 workflow-sync 派生表需与 `sprint.yaml` 正式范围一致。
- Sprint 关闭前的 stale scan 应阻断 archived Change 的 active path、待实现、待验收、旧归档路径和 stale `proposed` / `applied` 语义。
- 大型 Sprint 应优先消费 readiness / Fact Sheet 的 `change_batches` 摘要，再按 blocker、warning 或 evidence hint 读取必要原始 Change 文档。

## 已采纳内容

| 项 | 内容 | 采纳原因 |
|---|---|---|
| T1 | 最终输出契约卫生与校验脚本 | SoulKing 技能文件仍有可被照抄的占位模板风险，需要脚本化防回退。 |
| T2 | Sprint selection 脚本与测试 | 当前 Sprint 选择主要依赖规则文本，缺少确定性脚本。 |
| T3 | BUG review confirmed 根因门禁 | 现有根因规则未形成 approve 前硬阻断闭环。 |
| T4 | AI Usage unknown 矩阵语义、渲染和 scope 裁剪 | 复盘中需要区分未观测阶段与真实零消耗，避免成本矩阵误读。 |
| SPM1 | `sprint.md` 目标编号列表与 Scope 六列表头校验 | SoulKing 已有 Scope 校验，但缺少目标章节和主表结构防漂移。 |
| SPM2 | 已有 Sprint 范围更新的机器事实源优先规则 | 避免只手工编辑 `sprint.md` 或 marker block，导致 `sprint.yaml`、trace 与人读规划不一致。 |
| SPM3 | Sprint close stale scan 扩展 | 关闭 Sprint 前更早发现待验收、active path 和 legacy archive path 等过期事实。 |
| SPM4 | 大型 Sprint batch-first 读取策略 | 10+ Change 的归档和复核先看摘要，再按风险展开细节，降低上下文成本。 |

## 未采纳内容

- 未采纳 TilesFST 的业务领域示例、真实 release 数据、运行时数据和小程序/商品语境；SoulKing 只吸收工作流治理模式。
- 未采纳复制学习对象业务源码或部署配置；本次变更限定在治理资产、脚本和测试。
- 未采纳批量重写历史归档 Sprint 正文；本次只修正当前 active Sprint 中为通过新增门禁所需的目标编号列表。

## 替代方案与取舍

- 对 AI Usage 脚本采用项目无关的通用治理实现，并用 SoulKing 聚焦测试约束关键语义。
- 对命令输出契约采用统一尾部规则加少量命令专属示例，避免每个技能重复维护大段说明。
- 对 Sprint 选择先提供轻量校验脚本，不自动创建或迁移 Sprint；实际写入仍由 `/sprint-propose` 与 `add-sprint-scope-item.py` 控制。
- 对 `sprint.md` 校验采用兼容识别：支持 `## 1. 目标`、`## 1. Sprint 目标`、`Sprint 目标编号列表` 和既有“正式目标”列表；避免一次性强制重排历史文档。
- 对归档 stale scan 只强化与真实生命周期冲突的 blocker，不扫描无关历史归档，避免把治理脚本变成全仓文案审计。

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `AGENTS.md` | 更新命令最终输出契约入口摘要。 |
| `rules/agent-context-budget.md` | 增加输出契约卫生与校验脚本防回退说明。 |
| `rules/iterations-lifecycle.md` | 增加 Sprint 选择、连续编号和 active Sprint 数量门禁。 |
| `rules/bug-management.md` | 增加 BUG review approve 前 confirmed 根因要求。 |
| `rules/root-cause-evidence.md` | 增加 `/bug-review` confirmed 门禁和校验命令。 |
| `docs/README.md` | 增加 AI 命令输出契约摘要。 |
| `docs/08-command-execution-order.md` | 增加 Sprint selection 脚本和命令顺序入口。 |
| `.agents/skills/*/SKILL.md` | 统一最终输出契约，移除占位模板和通用示例风险。 |
| `.agents/skills/sprint-propose/SKILL.md` | 接入 Sprint selection gate 和项目化输出示例。 |
| `.agents/skills/sprint-archive/SKILL.md` | 强化 stale scan 和大型 Sprint batch-first 读取规则。 |
| `.agents/skills/bug-review/SKILL.md` | 接入 confirmed 根因 approve 前门禁。 |
| `.agents/skills/sprint-exps/SKILL.md` | 接入 AI Usage unknown 矩阵语义和 `--ai-usage-markdown` 渲染规则。 |
| `scripts/validate-agent-context-budget.py` | 增加最终输出契约卫生校验。 |
| `scripts/validate-sprint-selection.py` | 新增 Sprint 选择与连续编号校验脚本。 |
| `scripts/validate-sprint-scope.py` | 增加 `## 1. 目标` 编号列表、Scope 六列表头和关联 Change 目标覆盖校验。 |
| `scripts/sprint_close_stale_scan.py` | 增加 archived Change active path 和待验收文案 blocker。 |
| `scripts/validate-root-cause-evidence.py` | 增加 `--require-confirmed` 模式。 |
| `scripts/ai_usage.py` | 增加矩阵列观测状态与 Sprint scope 行裁剪。 |
| `scripts/generate-sprint-fact-sheet.py` | 增加矩阵写入门禁、`-` 渲染和 `--ai-usage-markdown` 输出。 |
| `tests/test_sprint_selection_validation.py` | 覆盖 Sprint selection 门禁。 |
| `tests/test_validate_root_cause_evidence.py` | 覆盖 confirmed 根因硬门禁。 |
| `tests/test_ai_usage.py` | 覆盖 AI Usage unknown 列状态和 scope 裁剪。 |
| `tests/test_generate_sprint_fact_sheet.py` | 覆盖 `-` 渲染和矩阵写入门禁。 |
| `tests/test_validate_sprint_scope.py` | 覆盖目标编号列表、短 Issue 别名和 Scope 六列表头校验。 |
| `tests/test_sprint_close_stale_scan.py` | 覆盖 archived Change active path 与待验收 stale scan。 |
| `openspec/changes/apply-tilesfst-workflow-quality-learnings/` | 承载本次治理变更 proposal、design、tasks 和 delta spec。 |
| `iterations/change/sprint-001/` | 将本 Change 纳入 Sprint scope，并补齐 `sprint.md` 目标编号列表以满足新增门禁。 |

## 产品影响

- API：不影响。
- 数据库：不影响。
- 前台 Web：不影响业务运行时代码。
- 后台管理端：不影响业务运行时代码。
- 桌面封装：不影响。
- 对象存储：不影响业务实现。
- Docker Compose：不影响。
- 测试：新增和更新治理脚本聚焦测试。

## 校验命令和结果

- `python -m py_compile scripts/validate-agent-context-budget.py scripts/validate-sprint-selection.py scripts/validate-root-cause-evidence.py scripts/ai_usage.py scripts/generate-sprint-fact-sheet.py`：通过。
- `uv run pytest tests/test_sprint_selection_validation.py tests/test_validate_root_cause_evidence.py tests/test_ai_usage.py tests/test_generate_sprint_fact_sheet.py`：通过，13 passed。
- `uv run pytest tests/test_validate_sprint_scope.py tests/test_sprint_close_stale_scan.py`：通过，4 passed。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-sprint-selection.py`：通过，当前默认使用 `sprint-001`。
- `python scripts/validate-root-cause-evidence.py --change apply-tilesfst-workflow-quality-learnings --json`：通过，未发现 linked BUG。
- `python scripts/generate-sprint-fact-sheet.py --sprint sprint-001 --summary`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate apply-tilesfst-workflow-quality-learnings --strict`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-tilesfst-workflow-quality-learnings`：通过。
- `python scripts/validate-doc-prose-hygiene.py <focused-paths>`：退出码 0，报告 2 条既有启发式 warning，未发现阻断项。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-workflow-quality-learnings --sprint auto`：通过，解析 Sprint 为 `sprint-001`。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-tilesfst-workflow-quality-learnings --sprint sprint-001 --json`：通过，`usage_mode=actual`，Sprint snapshot 已刷新。

## 学习对象只读保护

学习对象只执行 `sed`、`rg`、`find`、`git status --short`、`diff` 等读取命令；未在学习对象路径执行写入、安装、格式化、迁移、测试修复、提交、重置或清理操作。学习对象本身存在既有未提交 Issue 变更，本次未改动。

## 已知遗留提示

- Sprint Fact Sheet summary 仍提示历史 Change `study-projecttilesfst-governance-hardening` 在 `iterations/change/sprint-001/sprint.md` 中存在 archived path residual；该提示属于既有 Sprint 文档残留，不由本次 Change 引入。
