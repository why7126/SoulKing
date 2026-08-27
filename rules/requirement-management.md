---
purpose: 需求管理
content: REQ 文档、评审、OpenSpec 转换和验收约束
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 01:00:00
---

# 需求管理

- 新需求先使用 `/req-capture` 或 `/capture` 进入 `issues/requirements/plan/`。
- `/req-complete` 必须补齐背景、用户价值、范围、非目标、验收标准、影响面和测试策略。
- `/req-review <REQ-full-id>` 无 flag 时默认通过；通过后必须先 `/sprint-propose --req <REQ-full-id>` 纳入 Sprint，再 `/req-opsx <REQ-full-id>`。
- 需求链路的下一步命令必须保留完整 `REQ-xxxx-slug`，包括后续 `/opsx-apply <REQ-full-id>`、`/opsx-modify <REQ-full-id>`、`/opsx-archive <REQ-full-id>`。
- `issues/requirements/CHANGELOG.md` 应维护每个 REQ 一行的当前态看板索引，但机器事实源仍是 `_registry.yaml`、单条 `trace.md`、Sprint 四件套和 OpenSpec Change。

## 产品数据采集与链路观测门禁

需求涉及 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测时，REQ 文档必须读取并引用 `docs/standards/product-data-collection-observability.md`，并记录 `product_data_collection_observability` 适用状态、`affected_layers`、`reason` 和 `validation`。

若声明不适用，必须说明为什么不影响 API、DB、请求日志、行为事件、Task Trace、端请求封装、媒体链路或对象存储；不得只写“无”或“不涉及”。`/req-review` 应将缺少声明、验收项或 N/A 原因视为评审风险；`/req-opsx` 必须将该声明带入 Change。
