---
purpose: 数据库规范
content: SQLite、SQLAlchemy、迁移和运行时数据提交边界
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 01:00:00
---

# 数据库规范

- 表模型事实源为 `app/models.py`。
- 结构变更必须幂等，启动迁移需记录到 `_schema_migrations` 或等价机制。
- 不提交 `data/*.db`、`data/*.sqlite` 或真实用户数据。
- 涉及唯一约束、合并、对象键迁移时必须补充历史数据验证。

## 版本升级数据库证据

版本升级治理 MUST 区分“存在幂等 migration 代码”和“某条升级路径已验证”。当升级计划的数据库影响不是 `none`、`na`、`不涉及` 或等价无影响状态时，升级计划 MUST 要求：

- SQLite 数据目录或数据库文件的升级前备份责任和恢复方式。
- SQLAlchemy 模型与启动兼容迁移输入摘要。
- `_schema_migrations` 或等价版本记录。
- 升级后关键业务读写 smoke，例如登录、曲库查询、歌曲导入、播放/下载或歌词读写。
- DB 回滚边界：默认依赖升级前备份恢复或已验证的反向迁移策略。

不得仅凭脚本存在宣称生产 DB 升级安全。缺少 DB 备份或恢复责任时，升级计划 MUST 标记为 blocked 或 requires manual review。

## 产品数据采集与链路观测门禁

数据库变更若涉及 `usage_events`、`request_logs`、`task_traces`、`task_trace_spans`、日志索引、保留周期、脱敏字段、链路查询、播放/下载统计、导入任务追踪或对象存储观测字段，必须读取 `docs/standards/product-data-collection-observability.md`。

触发范围内的 Change 必须在设计、任务或验收材料中声明 `product_data_collection_observability` 适用层级，并同步 SQLAlchemy 模型、SQLite 迁移、数据库设计文档和测试；若某项不适用，必须记录具体 N/A 原因。
