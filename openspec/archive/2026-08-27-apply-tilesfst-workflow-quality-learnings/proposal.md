---
purpose: OpenSpec 提案
content: 应用 TilesFST 工作流质量治理学习项
created_at: 2026-08-27 00:00:00
updated_at: 2026-08-27 00:00:00
---

# 提案：应用 TilesFST 工作流质量治理学习项

## 背景

TilesFST 在 2026-08-22 至 2026-08-26 期间新增了多项工作流质量治理能力，覆盖 Sprint 选择、BUG review 根因 confirmed 门禁、AI Usage 矩阵语义和命令最终输出契约卫生。ProjectSoulKing 已具备部分基础规则，但缺少若干脚本化门禁、聚焦测试和输出契约卫生拦截。

## 变更范围

- 收紧命令最终输出契约，避免尖括号占位模板、无关通用示例和规范语气进入最终回复。
- 新增 Sprint 选择校验脚本和测试，约束 active Sprint 默认选择、连续编号和第三个 active Sprint 阻断。
- 为 BUG review approve 路径增加 `root_cause_status: confirmed` 硬门禁。
- 补强 AI Usage 矩阵的 `unknown` 语义、`-` 渲染、矩阵写入门禁和 Sprint scope 行裁剪。

## 非目标

- 不修改 `app/`、`app/static/`、`packaging/` 下业务运行时代码。
- 不复制 TilesFST 的业务领域规则、真实 release 数据、运行时数据或本地配置。
- 不改变后端 API、SQLite schema、前台 Web、后台管理端或对象存储业务实现。

## 验证

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-root-cause-evidence.py --bug <BUG-id> --require-confirmed` 的聚焦测试
- `python scripts/validate-sprint-selection.py`
- AI Usage 与 Sprint Fact Sheet 聚焦测试
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate apply-tilesfst-workflow-quality-learnings`
