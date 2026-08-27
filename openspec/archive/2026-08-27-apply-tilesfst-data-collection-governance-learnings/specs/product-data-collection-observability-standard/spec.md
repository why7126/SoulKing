## ADDED Requirements

### Requirement: 产品数据采集与链路观测治理标准

系统 SHALL 提供 ProjectSoulKing 版产品数据采集与链路观测标准，用于约束行为事件、请求日志、任务链路、流程节点、脱敏边界、保留周期和新变更接入清单。

#### Scenario: 标准文档作为详细事实源

- **WHEN** 变更涉及播放、下载、导入、歌词、歌单、头像、对象存储、后台管理、API 请求、数据库日志表或请求封装
- **THEN** 系统 SHALL 使用 `docs/standards/product-data-collection-observability.md` 作为详细事实源
- **AND** 入口规则、技能和索引 SHALL 只保留路径引用和门禁摘要

#### Scenario: 四层链路模型

- **WHEN** 设计产品数据采集或链路观测能力
- **THEN** 标准 SHALL 区分 `usage_events`、`request_logs`、`task_traces` 和 `task_trace_spans`
- **AND** SHALL 说明前台、后台、直接 API、后台任务和对象存储链路的可空规则
- **AND** SHALL 声明客户端字段不得作为认证、授权、审计身份或租户隔离依据

#### Scenario: 安全和脱敏边界

- **WHEN** 系统记录或展示采集数据、日志摘要或流程节点 metadata
- **THEN** 标准 SHALL 禁止保存 Authorization、Cookie、Token、密码、真实密钥、数据库 DSN、完整请求体、完整响应体、完整私有对象 key、完整签名 URL、本机绝对路径或真实用户敏感数据
- **AND** SHALL 要求后端持久化前执行脱敏、截断和安全序列化

### Requirement: 产品数据采集与链路观测流程门禁

系统 SHALL 在需求、OpenSpec、Sprint、实现和归档阶段要求触发范围内的变更声明数据采集与链路观测适用性、适用层级、N/A 原因和验证摘要。

#### Scenario: 触发范围声明

- **WHEN** REQ、BUG、Change、Sprint 或 diff 涉及 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装、对象存储或保留周期
- **THEN** 对应材料 SHALL 记录 `product_data_collection_observability`
- **AND** SHALL 包含 `affected_layers`、`reason` 和 `validation`

#### Scenario: 可审计 N/A

- **WHEN** 触发范围被判定为不适用
- **THEN** 声明 SHALL 使用 `status: not_applicable`
- **AND** `reason` SHALL 说明为什么不影响 API、DB、请求日志、行为事件、Task Trace、端请求封装、媒体链路或对象存储
- **AND** 不得只写“无”“不涉及”或等价空泛说明

#### Scenario: 聚焦校验

- **WHEN** 执行采集门禁校验脚本
- **THEN** 脚本 SHALL 检查标准文档、索引、规则和关键技能入口
- **AND** SHALL 支持按 Change、REQ、Sprint 或当前 diff 聚焦检查
- **AND** SHALL 默认避免扫描全部历史归档
- **AND** 失败输出 SHALL 只包含缺失文件、缺失字段、触发依据和修复建议摘要
