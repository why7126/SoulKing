---
created_at: 2026-08-21 00:00:00
updated_at: 2026-08-21 00:00:00
---

# 学习 deepseek-harness 治理加固

## 背景

用户确认应用 deepseek-harness 第一阶段学习候选 1、2、3、4、5：文档层级与一事实一归属、轻量决策记录、文档预算与文档杂质检查、最小相关验证选择、事故复盘标准。

ProjectSoulKing 已具备 OpenSpec、Sprint、`.agents/skills/`、`rules/`、`docs/spec-logs/` 和基础校验脚本，但文档事实归属、治理日志决策字段、文档治理自动检查、最小相关验证选择和 BUG 复盘触发条件仍偏分散。

## 变更目标

- 强化文档治理规则，明确文档层级、事实唯一归属、治理日志的决策记录字段和重复事实处理方式。
- 新增轻量文档治理校验脚本，检查长期 Markdown frontmatter、spec-log 隐私路径、AGENTS 字数预算和脚手架残留。
- 补充测试与交付验证规则，要求按影响面选择最小相关验证并在 Change 或报告中说明覆盖关系。
- 补充 BUG 复盘触发条件，引导系统性、隐蔽且高复现成本的问题进入知识库事故复盘。
- 生成 deepseek-harness 学习应用报告，并记录采纳、未采纳、影响面、验证和只读保护结果。

## 非目标

- 不引入 deepseek-harness 的双语文档配对机制、Agent Notes 目录树、Cordis 插件规范或 TypeScript monorepo 包约束。
- 不修改 `app/`、`app/static/`、`packaging/` 业务运行时代码。
- 不复制学习对象源码、长脚本、长规范或业务专属语境。

## 风险

- 文档治理检查可能暴露既有文档缺少 frontmatter、脚手架残留或本机路径泄漏，需要后续按范围修复。
- 最小相关验证规则需要 Agent 更清楚地解释验证与影响面的对应关系，短期内会增加交付说明成本。
