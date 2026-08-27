## 背景

本 Change 基于 `/spec-study TilesFST --focus 数据采集` 的候选项 D1-D4。TilesFST 的可迁移价值不是业务埋点实现，而是将“是否涉及数据采集和链路观测”变成需求、Change、Sprint、实现、归档和校验脚本都能识别的流程门禁。

SoulKing 的领域对象是歌曲、音频文件、歌词、歌单、用户资料、头像、播放/下载和对象存储。采集规范必须按这些边界重写，避免沿用 TilesFST 的商品、店主端、小程序、Orval 或 MySQL 生产语境。

## 目标与非目标

目标：

- 建立 `docs/standards/product-data-collection-observability.md` 作为详细事实源。
- 统一声明字段：`product_data_collection_observability`、`affected_layers`、`reason`、`validation`。
- 让 API、DB、日志审计、行为事件、播放/下载、媒体导入、对象存储、前台请求封装和后台请求封装相关变更必须声明采集适用性。
- 让 N/A 也可审计，必须说明不影响哪些层级，不能只写“无”或“不涉及”。
- 提供聚焦校验脚本，默认只看指定 Change、REQ、Sprint 或当前 diff，不全量扫描历史归档。

非目标：

- 不实现 `usage_events`、`request_logs`、`task_traces` 或 `task_trace_spans` 业务表。
- 不修改 `app/`、`app/static/`、`packaging/`、Docker Compose 或运行时数据。
- 不接入第三方埋点、APM、BI、实时告警或外部日志平台。
- 不批量修复历史 Change、历史 Issue 或历史 Sprint。

## 设计决策

### 决策 1：先标准和门禁，后业务实现

本 Change 只定义治理标准和检查路径。记录播放事件、下载日志、导入任务 trace 或后台审计查询属于业务能力，应通过独立 REQ / OpenSpec Change 进入实现链路。

### 决策 2：四层模型按 SoulKing 命名落地

标准采用通用四层：

```text
usage_events
  -> request_logs
      -> task_traces
          -> task_trace_spans
```

在 SoulKing 中，示例事件和任务改写为页面访问、歌曲搜索、播放、下载、导入扫描、歌词保存、歌单编辑、头像上传、对象迁移和后台批量治理。字段语义保持项目无关，业务示例保持音乐资产语境。

### 决策 3：入口只放摘要，详细规则单一归属

`AGENTS.md`、`rules/`、`.agents/skills/` 和 `docs/README.md` 只写触发范围、声明字段、N/A 要求和路径引用。详细字段、层级、脱敏、保留周期和验收清单只写在 `docs/standards/product-data-collection-observability.md`，避免长期文档漂移。

### 决策 4：校验脚本兼顾入口完整性和目标声明

脚本分两类检查：

- 标准完整性：确认标准文档、索引和相关 standards 交叉引用存在。
- 门禁完整性：确认入口规则、关键技能引用门禁；对指定 Change / REQ / Sprint / diff 检测触发词和路径，命中时检查声明块字段与 N/A 原因质量。

脚本只输出路径、缺失字段和摘要，不输出真实 `.env`、密钥、Cookie、Authorization header、运行时数据库内容、完整对象 key 或本机绝对路径。

## 产品数据采集与链路观测声明

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - workflow_governance
    - api
    - database
    - request_logs
    - usage_events
    - task_trace
    - frontend_request_wrapper
    - admin_request_wrapper
    - media_pipeline
    - object_storage
  reason: 本 Change 建立 SoulKing 数据采集与链路观测治理标准和流程门禁。
  validation: 运行采集规范标准校验、采集门禁校验、相关测试、OpenSpec 校验、目录校验、Workflow Sync 和 AI Usage hook。
```

## 风险与权衡

- 触发关键词可能误报：允许 `status: not_applicable`，但必须记录具体原因和验证摘要。
- 新增技能门禁会增加命令检查成本：通过入口摘要和脚本化检查减少手工展开。
- 业务采集能力仍不存在：这是刻意取舍；治理标准先稳定，后续业务实现独立排期。

## 回滚策略

归档前若门禁过宽或文档表达不适合 SoulKing，可在同一 Change 中调整触发词、适用层级和 N/A 判定；不得通过删除标准或跳过校验来规避失败。
