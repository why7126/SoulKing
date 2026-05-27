## REMOVED Requirements

### Requirement: 查询 AI 元数据建议是否可用

**Reason**: 产品决定移除基于 Dify 的元数据 AI 解析，不再提供工作流可用性探测。

**Migration**: 管理后台不再调用 `GET /admin/song-metadata/ai-parse/enabled`。元数据通过编辑抽屉手工填写并保存。

### Requirement: 未配置工作流时拒绝 AI 解析

**Reason**: 同上，AI 解析端点已删除。

**Migration**: 不再提供 `POST /admin/song-metadata/ai-parse`。

### Requirement: AI 解析须同时提供歌曲名与原唱

**Reason**: 同上。

**Migration**: 无替代 API；用户直接在表单中编辑歌曲名、原唱等字段。

### Requirement: 服务端代理外部工作流并返回规范化建议

**Reason**: 同上；`app/dify_workflow.py` 将删除。

**Migration**: 无。

### Requirement: 外部调用与工作流执行失败时的错误响应

**Reason**: 同上。

**Migration**: 无。

### Requirement: 管理后台对 AI 解析可用性的处理

**Reason**: 同上；编辑抽屉 AI 建议区与工具栏「AI 补全」将移除。

**Migration**: 使用既有元数据表单与「保存元数据」流程。

## MODIFIED Requirements

### Requirement: 外部集成规范范围（Purpose 对齐）

本规范所描述的「外部集成」能力 **不再包含** 任何出站 HTTP 工作流或元数据 AI 建议代理。对象存储（S3 兼容）的上传、读取与生命周期由「歌曲文件与对象存储生命周期」等规范定义，不属于本文件的实现范围。

#### Scenario: 部署不再要求工作流配置

- **GIVEN** 运维部署本应用
- **WHEN** 检查环境变量与后台功能清单
- **THEN** 无需配置 `DIFY_WORKFLOW_API_URL` 或 `DIFY_WORKFLOW_API_KEY`
- **AND** 管理后台不存在「开始 AI 解析」或「AI 补全」入口
