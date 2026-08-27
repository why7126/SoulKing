---
purpose: 产品数据采集与链路观测标准
content: ProjectSoulKing 行为事件、请求日志、任务链路、流程节点、保留周期、脱敏边界和新变更接入清单
created_at: 2026-08-27 00:43:58
updated_at: 2026-08-27 00:43:58
---

# 产品数据采集与链路观测标准

## 1. 目标

本标准约束 ProjectSoulKing 在后续引入行为事件、请求日志、任务链路、流程节点和日志审计能力时的字段语义、可信边界、脱敏要求、保留周期和验收口径。它是治理事实源，不代表当前已经实现所有表或采集能力。

适用范围：

| 层级 | 典型场景 |
|---|---|
| 前台 Web | 页面访问、歌曲搜索、筛选、播放、下载、歌单查看、歌词查看。 |
| 后台管理端 | 登录、歌曲管理、参考数据维护、用户管理、批量治理、导入扫描。 |
| 后端 API | 业务 API 请求摘要、认证上下文、耗时、状态、错误摘要。 |
| 媒体链路 | 音频导入、对象存储读写、封面或头像上传、播放和下载。 |
| 后台任务 | 扫描导入、对象键迁移、批量修复、发布或维护脚本。 |

若某个变更不适用其中一层，REQ、Change 或验收材料必须记录 N/A 原因。

## 2. 四层链路模型

```text
usage_events
  -> request_logs
      -> task_traces
          -> task_trace_spans
```

| 层级 | 事实源 | 说明 |
|---|---|---|
| 行为事件 | `usage_events` | 记录用户可命名行为，例如搜索、播放、下载、上传、保存、删除、登录成功或失败。 |
| 请求日志 | `request_logs` | 记录后端业务 API 请求摘要和服务端可信 `request_id`。 |
| 任务链路 | `task_traces` | 记录长耗时、多步骤、批量、后台或外部依赖任务的总体追踪。 |
| 流程节点 | `task_trace_spans` | 记录任务内部关键阶段，例如读取文件、解析元数据、写入对象存储、保存数据库、生成响应。 |

## 3. 入口规则

### 3.1 界面触发入口

前台或后台界面触发业务行为时，客户端可生成 `behavior_trace_id` 和 `behavior_event_id`，上报 `usage_events`，并在后续 API 请求中透传链路字段。后端保存 `request_logs` 时可记录 `behavior_trace_id` 和 `parent_behavior_event_id`，任务类请求再通过 `request_id` 进入 `task_traces`。

行为采集失败不得阻断播放、下载、保存、上传或其他主业务流程。

### 3.2 直接 API 和脚本入口

脚本、外部客户端或后台服务直接调用 API 时，不伪造 `usage_events`。后端仍生成 `request_id` 并记录请求摘要；任务类流程通过 `request_id` 或后台任务上下文进入 `task_traces`。无 HTTP 请求来源的后台任务允许 `parent_request_id` 为空。

## 4. 字段可信边界

| 字段 | 生成方 | 可信边界 |
|---|---|---|
| `behavior_trace_id` | 客户端 helper | 仅用于归因和排障，不得作为认证、授权、审计身份或租户隔离依据。 |
| `behavior_event_id` | 客户端 helper | 单条行为事件 ID，必须校验长度、字符集和格式。 |
| `parent_behavior_event_id` | 后端从请求头提取 | 仅用于请求日志回指行为事件，缺失时允许为空。 |
| `request_id` | 后端 middleware | 服务端可信单次请求 ID，客户端传入值不得覆盖。 |
| `client_request_id` | 客户端请求封装 | 用于排查重试和并发，不得作为服务端可信 ID。 |
| `task_trace_id` | 后端 helper | 后端生成或校验后接受，用于串联任务与流程节点。 |

所有客户端传入链路字段必须校验长度、字符集和格式。非法、超长或含敏感值的字段应被忽略或返回文档化错误。

## 5. 最小数据结构

### 5.1 `usage_events`

最小字段：`id`、`behavior_trace_id`、`behavior_event_id`、`event_name`、`event_category`、`client_type`、`page_path`、`session_id`、`actor_user_id`、`actor_role`、`properties`、`result`、`created_at`。

`event_name` 必须来自稳定事件字典，不得直接使用按钮文案、用户输入、歌词文本、文件名或搜索原文拼接。`properties` 只保存已脱敏摘要，例如对象类型、结果数量、筛选条件类别、播放来源或失败分类。

### 5.2 `request_logs`

最小字段：`id`、`request_id`、`behavior_trace_id`、`parent_behavior_event_id`、`client_request_id`、`method`、`path`、`route_template`、`status_code`、`result`、`duration_ms`、`client_type`、`actor_user_id`、`actor_role`、`resource_type`、`resource_id`、`metadata`、`created_at`。

健康检查、静态资源、OpenAPI 文档、预检 OPTIONS 和内部探活可排除。排除项必须写入规范、设计或实现文档。请求日志写入失败必须降级处理，不得覆盖主业务响应。

### 5.3 `task_traces`

最小字段：`id`、`task_trace_id`、`parent_request_id`、`task_type`、`task_name`、`status`、`started_at`、`finished_at`、`duration_ms`、`actor_user_id`、`client_type`、`metadata`、`error_code`、`error_message`、`created_at`。

建议接入场景：扫描导入、音频元数据解析、对象键迁移、批量治理、批量删除、发布维护、历史数据修复、复杂对象存储操作。

### 5.4 `task_trace_spans`

最小字段：`id`、`task_trace_id`、`span_id`、`parent_span_id`、`span_name`、`node_label`、`sequence`、`status`、`started_at`、`finished_at`、`duration_ms`、`metadata`、`error_code`、`error_message`、`created_at`。

流程节点命名应稳定，例如 `api_receive`、`input_validate`、`file_scan`、`metadata_parse`、`object_put`、`db_persist`、`playlist_update`、`response_build`。面向中文 UI 和验收文档时可展示为“流程节点”。

## 6. 应采集与可排除行为

应采集的可命名行为：

| 分类 | 示例 |
|---|---|
| 页面 | 前台曲库访问、后台页面访问、详情查看、Tab 切换。 |
| 查询 | 歌曲搜索、筛选、排序、加载更多、结果为空。 |
| 媒体 | 播放、暂停、下载、上传、导入扫描、对象读取失败。 |
| 内容 | 歌词保存、歌单创建、歌单编辑、参考数据维护。 |
| 认证 | 登录成功、登录失败、退出、密码修改。 |
| 管理 | 用户启停、批量治理、数据修复、发布维护。 |

可排除噪音：纯 hover、tooltip 关闭、无业务含义点击、重复无状态点击、不改变业务状态或查询条件的临时交互。

## 7. Task Trace 分级覆盖

满足以下任一条件的接口或任务应评估 Task Trace：

| 条件 | SoulKing 示例 |
|---|---|
| 长耗时 | 扫描本地导入目录、批量读取音频文件、对象迁移。 |
| 多步骤 | 导入歌曲同时解析元数据、写对象存储、建歌曲、建文件记录。 |
| 批量或后台任务 | 批量参考数据治理、历史对象键修复、发布维护脚本。 |
| 外部依赖 | MinIO 读写、签名 URL、外部媒体路径。 |
| 失败需定位节点 | 单条请求日志无法说明失败发生在扫描、解析、存储还是 DB。 |
| 高风险写操作 | 用户、认证、歌曲文件、歌词、歌单或对象存储批量修改。 |

普通简单读写可以只保留 `request_logs`，但 REQ、design 或验收材料必须说明 Task Trace N/A 原因。

## 8. 保留周期

默认保留周期：

| 数据 | 默认周期 | 处理方式 |
|---|---:|---|
| `request_logs` 明细 | 90 天 | 超期删除或匿名化。 |
| `usage_events` 明细 | 180 天 | 超期删除或匿名化。 |
| `task_traces` / `task_trace_spans` 明细 | 90 天 | 超期删除或匿名化。 |
| 聚合数据 | 1 年 | 可用于长期趋势和容量分析。 |

调整保留周期时必须说明原因、影响范围、审批依据、存储成本、排障窗口、隐私风险和回滚方式。

## 9. 安全与脱敏

禁止采集或展示：

- Authorization。
- Cookie。
- Token。
- 密码。
- 真实密钥。
- 数据库 DSN。
- MinIO AccessKey / SecretKey。
- 完整请求体。
- 完整响应体。
- 完整私有对象 key。
- 完整签名 URL。
- 本机绝对路径。
- 真实用户敏感数据。

前端脱敏只能作为展示优化。安全边界必须在后端持久化前完成敏感字段过滤、长度截断和安全 JSON 序列化。

## 10. 新变更接入清单

触发 API、DB、日志审计、行为事件、Task Trace、前台请求封装、后台请求封装、媒体导入、播放下载或对象存储链路时，REQ、Change 或验收材料必须记录：

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - api
    - database
    - request_logs
    - usage_events
    - task_trace
    - frontend_request_wrapper
    - admin_request_wrapper
    - media_pipeline
    - object_storage
  reason: 说明本变更为什么触发采集或链路观测门禁。
  validation: 说明已运行或计划运行的采集、日志、脱敏、保留周期、API、DB、UI 或 N/A 校验。
```

不适用时：

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 说明为什么不影响 API、DB、请求日志、行为事件、Task Trace、端请求封装、媒体链路或对象存储。
  validation: 说明如何确认不适用。
```

## 11. 验证命令

标准文档和索引引用校验：

```bash
python scripts/validate-product-data-observability-standard.py
```

门禁聚焦校验：

```bash
python scripts/validate-product-data-observability-gates.py --change <change-id>
python scripts/validate-product-data-observability-gates.py --req <REQ-id>
python scripts/validate-product-data-observability-gates.py --sprint <sprint-id>
python scripts/validate-product-data-observability-gates.py --diff
```
