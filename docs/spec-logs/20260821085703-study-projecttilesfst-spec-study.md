---
purpose: ProjectTilesFST spec-study 学习应用报告
content: 日志优先学习、漂移复核、学习报告取舍字段、文档表达卫生和最小相关验证矩阵
created_at: 2026-08-21 08:57:03
updated_at: 2026-08-21 08:57:03
---

# ProjectTilesFST spec-study 学习应用报告

## 学习对象与模式

- 学习对象：ProjectTilesFST。
- 学习模式：Phase 1 本地只读学习，Phase 2 经用户确认应用 S1-S5。
- 执行时间：2026-08-21 08:57:03，时区 `Asia/Shanghai`。
- 应用 Change：`apply-projecttilesfst-spec-study-enhancements`。
- 承载 Sprint：`sprint-001`。

## 学习到的治理能力

- 日志优先学习：学习对象存在 spec-log 索引时，先把它作为治理演进入口地图。
- 日志漂移复核：日志描述不能替代真实资产、active Change、Sprint 四件套或正式规格。
- 学习报告决策字段：记录采纳、未采纳、替代方案或取舍、验证责任和后续触发条件。
- 文档表达卫生：长期文档避免会话推理、临时草稿、review 对话、不可解析路径和不必要历史叙事。
- 最小相关验证：按触达范围选择验证矩阵，不机械重复与本次 diff 无关的检查。

## 已采纳内容和采纳原因

| 内容 | 采纳原因 | 落地位置 |
|---|---|---|
| S1 日志优先学习 | 减少无差别扫仓库，并利用治理日志快速定位演进脉络 | `.agents/skills/spec-study/SKILL.md`、`AGENTS.md` |
| S2 日志漂移复核 | 防止历史日志替代当前事实源 | `.agents/skills/spec-study/SKILL.md`、OpenSpec delta |
| S3 学习报告取舍字段 | 让跨项目学习可解释、可复核 | `.agents/skills/spec-study/SKILL.md`、`rules/document-governance.md` |
| S4 文档表达卫生 | 降低会话残留和隐私路径进入长期文档的风险 | `docs/standards/document-prose-hygiene.md`、`scripts/validate-doc-prose-hygiene.py` |
| S5 最小相关验证矩阵 | 让治理命令验证范围与触达面匹配 | `docs/08-command-execution-order.md` |

## 未采纳内容和未采纳原因

- 未迁移 ProjectTilesFST 的 `src/`、React、微信小程序、MySQL、Orval 或生产部署语境；ProjectSoulKing 当前业务边界是 `app/`、`app/static/`、SQLite 和 MinIO。
- 未恢复 `.cursor/`、`.codex/`、`.kiro/`、`.opencode/` 或 `.claude/`；ProjectSoulKing 当前唯一 Agent 入口是 `.agents/skills/`。
- 未原样复制 ProjectTilesFST 长脚本或长规范；本次按 ProjectSoulKing 语境改写为短规则、标准文档和轻量脚本。

## 替代方案或取舍

- 用 `docs/spec-logs/` 的单份学习报告承载决策记录，避免新增 Agent notes 目录。
- 文档表达卫生脚本先作为 warning 级启发式检查，不作为自动删除或强阻断门禁。
- 命令顺序文档承载验证矩阵，不额外新建平行治理目录。

## 验证责任和后续触发条件

- 修改长期文档、规则、技能说明或知识库的治理命令负责运行聚焦文档卫生校验。
- OpenSpec、目录结构、Sprint scope、Workflow Sync 和 AI Usage 仍由对应 workflow 命令负责。
- 若文档卫生脚本 warning 噪声过多，应通过独立治理 Change 调整 pattern、allowlist 或默认扫描范围。

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `.agents/skills/spec-study/SKILL.md` | 固化日志优先学习、漂移复核、事实唯一归属、报告取舍字段和文档卫生校验建议 |
| `AGENTS.md` | 增加文档治理读取路由、spec-study 日志优先学习摘要和长期文档表达红线 |
| `rules/document-governance.md` | 补充事实唯一归属、文档表达卫生和治理决策字段 |
| `docs/08-command-execution-order.md` | 补充最小相关验证原则和治理脚本门禁矩阵 |
| `docs/standards/document-prose-hygiene.md` | 新增长期文档表达卫生标准 |
| `scripts/validate-doc-prose-hygiene.py` | 新增 warning 级启发式校验脚本 |
| `docs/README.md` | 同步文档索引 |
| `docs/spec-logs/CHANGELOG.md` | 登记本次跨项目学习应用 |
| `openspec/changes/apply-projecttilesfst-spec-study-enhancements/` | 承载 proposal、design、tasks 和 delta spec |
| `iterations/change/sprint-001/sprint.yaml` | 将纯治理 Change 纳入 Sprint scope |

## 影响范围

- API：不影响。
- 数据库：不影响。
- 前台 Web：不影响业务实现。
- 后台管理端：不影响业务实现。
- 桌面封装：不影响。
- 对象存储：不影响。
- Docker Compose：不影响。
- 测试：新增治理脚本级校验；业务测试不适用。

## 校验命令和结果

- `python scripts/validate-doc-prose-hygiene.py <focused-paths> --json`：通过执行，返回 warning 9 条；命中项主要是标准文档中的反例词和命令文档中的规范性触达范围表述，未作为 blocker。
- `python -m py_compile scripts/validate-doc-prose-hygiene.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate apply-projecttilesfst-spec-study-enhancements`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-projecttilesfst-spec-study-enhancements --sprint auto`：通过，解析 Sprint 为 `sprint-001`，Updated 2，Errors 0。
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-projecttilesfst-spec-study-enhancements`：通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-projecttilesfst-spec-study-enhancements --sprint sprint-001 --json`：通过，`status=ok`，`warning_count=0`。
- `git diff --name-only -- app app/static packaging`：显示工作区存在前置业务改动；本次学习应用未编辑 `app/`、`app/static/` 或 `packaging/` 文件。

## 学习对象只读保护结果

对 ProjectTilesFST 仅执行只读扫描、片段读取、diff 对照和 Git 状态查询；未在学习对象路径中执行写入、安装、生成、格式化、迁移、测试修复、清理、提交、切换分支或修改 Git 状态的操作。学习对象本身存在既有未提交变更，本次未处理。

## 后续建议

- 文档表达卫生脚本先作为辅助校验使用；积累误报后再决定是否升级为更强门禁。
- 后续 `/spec-opt` 若也触达长期文档，可复用同一文档卫生检查规则。
