---
purpose: 文档索引
content: ProjectSoulKing 长期文档导航和文档层级说明
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 00:00:00
---

# ProjectSoulKing 文档索引

## 文档层级

ProjectSoulKing 的文档遵守“一事实一归属”：`AGENTS.md` 只放每次会话都需要的站立规则，`rules/` 放强制工程规则，`docs/` 放长期产品与技术说明，`docs/standards/` 放可复用标准，`docs/knowledge-base/` 放复盘和经验，`docs/spec-logs/` 放治理变更报告和学习记录。跨层引用应使用相对链接，不复制完整规则。

AI 命令最终输出必须使用真实「下一步」和「待用户决策/处理」结果；技能契约不得提供可被原样输出的尖括号占位模板、通用 BUG 示例或规范语气，且不得在待处理事项中重复下一步命令。

| 文档 | 内容 |
|---|---|
| [00-product-overview.md](00-product-overview.md) | 产品定位、用户、能力与范围 |
| [01-architecture.md](01-architecture.md) | 架构、模块、数据流和关键边界 |
| [02-deployment.md](02-deployment.md) | 本地启动、Docker、ProjectMinio 依赖 |
| [03-api-index.md](03-api-index.md) | REST API 分组索引 |
| [04-database-design.md](04-database-design.md) | SQLite 表与迁移策略 |
| [05-compatibility-matrix.md](05-compatibility-matrix.md) | 浏览器、数据库、对象存储兼容性 |
| [07-object-storage-strategy.md](07-object-storage-strategy.md) | MinIO 单桶和对象键策略 |
| [08-command-execution-order.md](08-command-execution-order.md) | REQ/BUG、Sprint、OpenSpec、发布、镜像和产品手册命令顺序与默认评审语义 |
| [standards/](standards/) | API、认证、测试、上传、媒体资产验收等标准 |
| [standards/api-governance.md](standards/api-governance.md) | API 变更、文档和兼容要求 |
| [standards/authentication.md](standards/authentication.md) | 鉴权和权限边界标准 |
| [standards/testing-governance.md](standards/testing-governance.md) | 测试治理、最小相关证据和根因证据校验 |
| [standards/product-data-collection-observability.md](standards/product-data-collection-observability.md) | 产品数据采集、请求日志、任务链路、流程节点、保留周期和脱敏边界 |
| [standards/file_upload.md](standards/file_upload.md) | 文件上传标准 |
| [standards/media-asset-acceptance-template.md](standards/media-asset-acceptance-template.md) | 音频、歌词、封面、头像和对象存储链路验收模板 |
| [standards/prototype-ui-acceptance.md](standards/prototype-ui-acceptance.md) | 带 prototype 的 UI Change 验收证据标准 |
| [standards/document-prose-hygiene.md](standards/document-prose-hygiene.md) | 长期文档表达卫生与不可解析引用审计标准 |
| [knowledge-base/](knowledge-base/) | Sprint 复盘、事故和最佳实践 |
| [spec-logs/CHANGELOG.md](spec-logs/CHANGELOG.md) | 规范工程变更历史索引，汇总 `/spec-study` 学习报告与 `/spec-opt` 治理迭代日志 |
