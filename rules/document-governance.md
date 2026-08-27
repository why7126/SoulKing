---
purpose: 文档治理
content: Markdown 元数据、更新时间、事实源归属和治理日志规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 01:00:00
---

# 文档治理

- 新增长期 Markdown 文档应包含 YAML Frontmatter：`purpose`、`content`、`created_at`、`updated_at`。
- 时间统一 `YYYY-MM-DD HH:mm:ss`，默认 `Asia/Shanghai`。
- 更新文档只更新 `updated_at`，除非文档被重新创建。
- 需求和 BUG 不写入 `docs/` 根目录，应进入 `issues/requirements/` 或 `issues/bugs/`。
- 长期文档不得残留脚手架标记、脚手架输入表或散落占位。
- 长期事实 MUST 只有一个事实源；`AGENTS.md`、`rules/`、`docs/standards/`、`.agents/skills/` 和 `docs/spec-logs/` 之间不得复制完整规则正文，入口文件只保留短摘要和相对链接。
- 新增或更新长期文档 SHOULD 遵守 `docs/standards/document-prose-hygiene.md`，避免会话推理、临时草稿、review 对话、不可解析引用和不必要历史叙事进入长期文档。
- 治理类 Change、`/spec-study` 学习报告和 `/spec-opt` 治理日志 SHOULD 记录已采纳原因、未采纳原因、替代方案或取舍、验证责任和后续触发条件。
- 产品数据采集与链路观测的详细事实源为 `docs/standards/product-data-collection-observability.md`；入口规则、技能和索引只写触发范围、声明字段和路径引用，不得复制完整字段模型。
- 触发采集门禁的 REQ、Change、Sprint 或验收材料应记录 `product_data_collection_observability`、`affected_layers`、`reason` 和 `validation`；N/A 也必须说明具体不适用原因。
- 文档新增、重构或治理变更交付前 SHOULD 运行 `python scripts/validate-doc-governance.py`；未运行时必须说明不适用原因。
