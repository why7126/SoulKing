---
purpose: 语言规范
content: 文档、注释、API 名称和回复语言边界
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# 语言规范

- AI 回复、OpenSpec 文档、需求、BUG、Sprint 文档默认使用简体中文。
- 代码标识符、API 路径、文件路径、命令、环境变量保持原文。
- 技术术语如 API、REST、JWT、Cookie、MinIO、SQLite 可保留英文。
- 面向用户的 UI 文案应保持简洁、一致，避免中英文混杂长句。
- OpenSpec CLI 或上游 schema 若在归档时提示 `proposal.md` 缺少 `## Why` / `## What Changes` 等英文标准标题，该提示在本项目中属于 CLI 兼容性提示；项目阻塞门禁以 `python scripts/validate-openspec-language.py` 为准，不得为消除提示回填英文脚手架标题。
- 运行 OpenSpec 文档校验时 MUST 执行 `python scripts/validate-openspec-language.py` 或等价命令；归档前 active Change 不得存在英文脚手架标题或全英文任务项。
