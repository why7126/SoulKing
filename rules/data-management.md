---
purpose: 数据管理
content: 本地数据、测试数据、导入目录和敏感信息规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 01:00:00
---

# 数据管理

- `data/` 用于本地 SQLite、调试数据和临时运行文件。
- `import/` 用于本地待导入媒体。
- 真实数据、媒体、密钥和会话材料不得提交。
- 测试夹具应放在 `tests/fixtures/`，并使用最小可公开样例。
- 采集数据、请求日志、任务链路和流程节点不得保存真实密钥、Token、Cookie、完整请求体、完整响应体、完整私有对象 key、完整签名 URL、本机绝对路径或真实用户敏感数据；详细边界见 `docs/standards/product-data-collection-observability.md`。
- 涉及播放、下载、导入、媒体链路或对象存储观测的变更必须声明 `product_data_collection_observability` 适用层级、N/A 原因和验证摘要。
