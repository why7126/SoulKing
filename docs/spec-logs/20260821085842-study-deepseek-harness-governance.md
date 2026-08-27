---
created_at: 2026-08-21 08:58:42
updated_at: 2026-08-21 08:58:42
---

# deepseek-harness 治理学习应用报告

## 学习对象

- 学习对象：`deepseek-ai/deepseek-harness`
- 学习模式：`auto`
- 执行时间：2026-08-21 08:58:42 Asia/Shanghai
- 应用 Change：`study-deepseek-harness-governance-hardening`

## 学习到的治理能力

- 文档层级与一事实一归属：入口只放站立规则，事实源放在 owning 文档，其他位置链接引用。
- 决策记录：治理变更需要记录采纳原因、未采纳原因、替代方案、影响和验证证据。
- 文档治理门禁：用脚本检查 frontmatter、文档预算、脚手架残留和隐私路径。
- 最小相关验证：按影响面选择验证命令，并说明命令覆盖的风险。
- 事故复盘：系统性、隐蔽、高复现成本缺陷需要沉淀防线缺口和预防动作。

## 已采纳内容

- 采纳文档层级和一事实一归属，原因是 ProjectSoulKing 已有 `AGENTS.md`、`rules/`、`docs/`、`docs/spec-logs/`，适合通过归属规则减少重复事实。
- 采纳轻量决策记录，原因是本项目已有 OpenSpec Change 和 spec-log 报告，不需要新增平行 Agent Notes 目录。
- 采纳文档治理脚本，原因是 frontmatter、脚手架残留、隐私路径和文档预算可通过只读脚本低成本检查。
- 采纳最小相关验证选择，原因是当前项目既有 Python、静态 Web、Docker、Mintlify 和治理脚本多种影响面，不宜默认全量验证。
- 采纳事故复盘触发标准，原因是 BUG 链路已有根因和验证记录，但缺少何时沉淀知识库事故复盘的门槛。

## 未采纳内容

- 未采纳完整双语文档配对机制：本项目默认中文，维护成本高于当前收益。
- 未采纳 `.agents/notes/` 全量生命周期树：本项目已有 OpenSpec、Sprint 和 spec-log 事实源，新增目录会制造平行治理资产。
- 未采纳 Cordis 插件、TypeScript monorepo package invariant 和发布矩阵：与 FastAPI、SQLite、MinIO、静态 Web 架构不匹配。
- 未采纳学习对象的长脚本或长规范原文：本次只按 ProjectSoulKing 边界改写可迁移规则。

## 更新文件清单

- `openspec/changes/study-deepseek-harness-governance-hardening/proposal.md`：记录治理学习应用目标、非目标和风险。
- `openspec/changes/study-deepseek-harness-governance-hardening/design.md`：记录项目化改写方案和校验策略。
- `openspec/changes/study-deepseek-harness-governance-hardening/tasks.md`：记录任务进度。
- `openspec/changes/study-deepseek-harness-governance-hardening/specs/governance-workflow-tooling/spec.md`：补充治理工作流能力 delta spec。
- `iterations/change/sprint-001/sprint.yaml`：将本 Change 纳入 Sprint scope。
- `rules/document-governance.md`：补充一事实一归属、轻量决策记录和文档治理校验规则。
- `docs/README.md`：补充文档层级说明。
- `rules/testing.md`：补充最小相关验证原则。
- `docs/standards/testing-governance.md`：补充验证命令与影响面对应关系。
- `rules/bug-management.md`：补充事故复盘触发条件。
- `rules/directory-structure.md`：补充文档治理检查边界。
- `scripts/validate-directory-structure.py`：纳入新增文档治理脚本。
- `scripts/validate-doc-governance.py`：新增只读文档治理校验脚本。
- `docs/spec-logs/CHANGELOG.md`：追加本次学习应用索引。

## 影响面

- API：无影响。
- 数据库：无影响。
- 前台 Web：无影响。
- 后台管理端：无影响。
- 桌面封装：无影响。
- 对象存储：无影响。
- Docker Compose：无影响。
- 测试：新增治理文档校验脚本，并补充最小相关验证规则。

## 校验结果

- `python scripts/validate-doc-governance.py`：通过，55 个长期 Markdown 已检查。
- `python -m py_compile scripts/validate-doc-governance.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过，36 个命令技能和 49 个技能输出契约已检查。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate study-deepseek-harness-governance-hardening`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change study-deepseek-harness-governance-hardening --sprint auto`：通过，解析到 `sprint-001`。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change study-deepseek-harness-governance-hardening --sprint sprint-001 --json`：通过，AI Usage Sprint snapshot 已刷新。

## 学习对象只读保护

学习对象使用临时只读快照读取；本次应用未对学习对象执行写入、安装依赖、格式化、迁移、测试修复、提交、重置或清理操作。复核学习对象 Git 状态为空。

## 后续建议

- 后续治理变更可继续使用 `scripts/validate-doc-governance.py` 作为文档类最小相关验证。
- 若未来文档数量明显增长，再评估是否需要更细的文档预算 manifest；当前保持轻量脚本即可。
