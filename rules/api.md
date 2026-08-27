---
purpose: API 规范
content: REST 路由、响应兼容、认证和文档同步要求
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 01:00:00
---

# API 规范

- API 路由由 FastAPI 暴露，文档入口为 `/docs`。
- 受保护业务 API 必须经过登录 Cookie 或管理员权限校验。
- 修改请求/响应字段时同步 `app/schemas.py`、前端调用、OpenSpec 和 `docs/03-api-index.md`。
- 播放、下载、头像等资源接口必须保护对象存储真实地址和签名 URL 安全。

## 产品数据采集与链路观测门禁

API 变更若涉及请求头、请求日志、行为事件、链路 ID、Task Trace、错误码、响应字段、播放/下载、媒体导入、对象存储观测或前后台请求封装，必须读取 `docs/standards/product-data-collection-observability.md`。

触发范围内的 REQ、OpenSpec Change、tasks、acceptance 或 trace 必须记录 `product_data_collection_observability` 或等价固定声明，至少包含适用状态、`affected_layers`、`reason` 和 `validation`。若不适用，必须说明为什么不影响 API、`request_logs`、`usage_events`、Task Trace、端请求封装、媒体链路或对象存储；不得只写“无”或“不涉及”。
