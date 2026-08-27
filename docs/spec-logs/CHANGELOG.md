---
purpose: 规范工程变更历史
content: ProjectSoulKing 规范、脚本、命令和治理文档更新日志索引
created_at: 2026-08-08 20:57:51
updated_at: 2026-08-27 01:10:11
---

# 规范工程变更历史

本文件是 `docs/spec-logs/` 的累计变更历史索引，用于记录每一次规范、脚本、命令和治理流程更新。单次详细报告仍按同目录时间戳文件沉淀：

- `/spec-study` 学习报告：`YYYYMMDDhhmmss-study-xxx.md`
- `/spec-opt` 治理日志：`YYYYMMDDhhmmss-governance-xxx.md`

## 记录规则

- 每次 `/spec-study` 或 `/spec-opt` 更新治理资产后，追加一条变更历史记录。
- 记录摘要应覆盖变更目标、影响范围、详细日志和验证结果。
- `其他项目落地提示词` 列记录其他项目复用该规范时可直接使用或按项目替换的 Prompt。
- 影响范围可使用 `AGENTS`、`skills`、`rules`、`docs`、`scripts`、`OpenSpec`、`Sprint`、`deploy`、`Mintlify`、`release` 等标签。
- 不得记录真实 env 内容、密钥、访问令牌、真实用户数据、本机绝对路径、未脱敏日志、聊天原文、工单原文、截图个人信息或学习对象源码。
- 详细过程、候选方案和完整验证证据应放入同目录时间戳日志；本文件只保留可检索的历史索引。

## 变更历史

| 时间 | 类型 | 主题 | 摘要 | 影响范围 | 详细记录 | 验证 | 其他项目落地提示词 |
|---|---|---|---|---|---|---|---|
| 2026-08-27 00:43:58 | study | tilesfst-data-collection | 学习并应用 TilesFST 的产品数据采集与链路观测标准、流程门禁、技能检查和聚焦校验脚本。 | AGENTS, skills, rules, docs, scripts, tests, OpenSpec, Sprint | [20260827004358-study-tilesfst-data-collection.md](20260827004358-study-tilesfst-data-collection.md) | 脚本编译、聚焦 pytest、采集标准、采集门禁、上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope、文档卫生、Workflow Sync 和 AI Usage hook 通过；文档卫生仅启发式 warning | `/spec-study apply TilesFST --items D1,D2,D3,D4；按当前项目语境落地产品数据采集标准、流程门禁、声明字段、N/A 原因和聚焦校验脚本，必须通过 OpenSpec Change 与 Sprint scope 承载。` |
| 2026-08-27 00:19:14 | study | tilesfst-workflow-quality | 学习并应用 TilesFST 的命令最终输出契约卫生、Sprint selection、BUG review confirmed 根因门禁、AI Usage unknown 矩阵语义，以及 sprint.md 正式目标、Scope 六列表头、归档 stale scan 和大型 Sprint batch-first 治理。 | AGENTS, skills, rules, docs, scripts, tests, OpenSpec, Sprint | [20260827001914-study-tilesfst-workflow-quality.md](20260827001914-study-tilesfst-workflow-quality.md) | 脚本编译、聚焦 pytest、上下文预算、Sprint selection、根因证据、OpenSpec 语言、目录结构、目标 Change、Sprint scope、文档卫生、Workflow Sync 和 AI Usage hook 通过；文档卫生仅启发式 warning | `/spec-study apply TilesFST --items T1,T2,T3,T4,SPM1,SPM2,SPM3,SPM4；按当前项目语境落地输出契约卫生、Sprint 选择门禁、BUG review confirmed 根因门禁、AI Usage unknown 矩阵语义、sprint.md 目标/Scope 校验、归档 stale scan 和大型 Sprint batch-first 规则，必须通过 OpenSpec Change 与 Sprint scope 承载。` |
| 2026-08-21 22:50:52 | study | tilesfst-governance-upgrade | 学习并应用 TilesFST 的版本升级路径、证据化根因、音乐媒体资产验收模板和文档索引补强。 | AGENTS, skills, rules, docs, scripts, OpenSpec, Sprint, release | [20260821225052-study-tilesfst-governance-upgrade.md](20260821225052-study-tilesfst-governance-upgrade.md) | 脚本编译、升级计划临时样例、根因证据、上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope、文档治理、Workflow Sync 通过；AI Usage hook 因缺少 token_count 事件返回 warning | `/spec-study apply TilesFST --items U1,R1,M1,D1；按当前项目语境落地升级路径计划、根因证据、音乐媒体验收模板和文档索引补强，必须通过 OpenSpec Change 与 Sprint scope 承载。` |
| 2026-08-21 13:46:22 | governance | review-default-approval | 将 `/req-review` 与 `/bug-review` 的无 flag 行为定义为默认通过，非通过结论改为显式 flag，并同步命令顺序和下一步示例。 | skills, rules, docs, OpenSpec, Sprint | [20260821134622-governance-review-default-approval.md](20260821134622-governance-review-default-approval.md) | 上下文预算、OpenSpec 语言、目录结构、文档治理、文档卫生、OpenSpec validate、Sprint scope、Workflow Sync 和 AI Usage Hook 通过 | `/spec-opt 将 bug-review 和 req-review 改为无 flag 默认 approve，仅 reject/defer/wont-fix 需要显式 flag，并同步命令顺序与下一步示例` |
| 2026-08-21 08:58:42 | study | deepseek-harness-governance | 学习并应用 deepseek-harness 的文档层级、一事实一归属、轻量决策记录、文档治理校验、最小相关验证和事故复盘标准。 | rules, docs, scripts, OpenSpec, Sprint | [20260821085842-study-deepseek-harness-governance.md](20260821085842-study-deepseek-harness-governance.md) | 文档治理、脚本编译、上下文预算、OpenSpec 语言、目录结构、OpenSpec validate、Workflow Sync 和 AI Usage Hook 通过 | `/spec-study apply deepseek-harness --focus document-governance,decision-records,doc-validation,relevant-checks,incident-postmortem` |
| 2026-08-21 08:57:03 | study | projecttilesfst-spec-study | 应用 ProjectTilesFST 的 spec-study 增强项，补强日志优先学习、日志漂移复核、学习报告取舍字段、文档表达卫生和最小相关验证矩阵。 | AGENTS, skills, rules, docs, scripts, OpenSpec, Sprint | [20260821085703-study-projecttilesfst-spec-study.md](20260821085703-study-projecttilesfst-spec-study.md) | 文档卫生、脚本编译、上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope、Workflow Sync 和 AI Usage Hook | `/spec-study apply ProjectTilesFST --focus spec-study --items S1,S2,S3,S4,S5；按当前项目语境落地日志优先学习、漂移复核、学习报告取舍字段、文档表达卫生和最小相关验证矩阵，必须通过 OpenSpec Change 与 Sprint scope 承载。` |
| 2026-08-10 23:38:48 | study | projectmoonbox-governance | 学习并应用 ProjectMoonBox 的命令顺序、Git 安全检查、Issues 当前态看板、原型 UI 验收和 Agent 上下文预算治理。 | AGENTS, skills, rules, docs, scripts, OpenSpec, Sprint | [20260810233848-study-projectmoonbox-governance.md](20260810233848-study-projectmoonbox-governance.md) | 上下文预算、OpenSpec 语言、目录结构、git-check 和 OpenSpec validate 通过 | `/spec-study apply ProjectMoonBox --focus command-execution-order,git-check,issues-changelog-current-state,prototype-ui-acceptance,agent-context-budget` |
| 2026-08-08 21:02:26 | governance | spec-logs-adoption-prompt | 为变更历史列表新增 `其他项目落地提示词` 列，记录跨项目复用规范时可使用的 Prompt。 | docs | [20260808210226-governance-spec-logs-adoption-prompt.md](20260808210226-governance-spec-logs-adoption-prompt.md) | 目录、文档、Agent 上下文和 OpenSpec 语言校验通过 | `/spec-opt 在 docs/spec-logs/CHANGELOG.md 的变更历史表中新增“其他项目落地提示词”列，用于记录每次规范/脚本/命令更新如何在本项目落地复用的 Prompt，并补充本次治理日志。` |
| 2026-08-08 20:57:51 | governance | spec-logs-changelog | 新增规范工程变更历史索引，明确规范、脚本、命令和治理流程更新的累计记录方式。 | docs, rules | [20260808205751-governance-spec-logs-changelog.md](20260808205751-governance-spec-logs-changelog.md) | 目录、文档、Agent 上下文和 OpenSpec 语言校验通过 | `/spec-opt 在 docs/spec-logs/ 下新增规范工程变更历史文档，用于记录每一次规范、脚本、命令和治理流程更新日志，并同步文档索引与目录规范。` |
| 2026-08-07 12:17:33 | study | projecttilesfst-spec-governance | 学习并应用 ProjectTilesFST 的 spec-opt/spec-study、上下文预算、目录、deploy、Mintlify 和 release 治理经验。 | AGENTS, skills, rules, docs, scripts, OpenSpec, Sprint, deploy, Mintlify, release | [20260807121733-study-projecttilesfst-spec-governance.md](20260807121733-study-projecttilesfst-spec-governance.md) | 目录、OpenSpec、Agent、Mintlify 和 release 校验通过 | `/spec-study apply <参考项目名> --focus agent-context-budget,directory-structure,deploy-mintlify-release；结合本项目实际情况同步适合的规范、技能、脚本和命令，不修改参考项目代码。` |
