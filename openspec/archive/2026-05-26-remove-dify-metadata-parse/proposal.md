## Why

后台「歌曲元数据 AI 解析」依赖外部 Dify 工作流（环境变量配置、服务端代理、编辑抽屉与工具栏入口）。该能力使用频率低、维护成本高（独立模块、专用 API、大量前端状态），且与歌词/播放/入库等核心路径无关。移除后可简化部署（无需 `DIFY_*` 配置）、减少死代码与规范漂移，元数据仍通过编辑抽屉手工维护。

## What Changes

- **BREAKING**：删除 `GET /admin/song-metadata/ai-parse/enabled` 与 `POST /admin/song-metadata/ai-parse` API。
- 删除 `app/dify_workflow.py` 及 `main.py` 中对 Dify 的调用；移除 `config` / `.env.example` 中全部 `DIFY_*` 配置项。
- 删除 `schemas` 中 `SongMetadataAiParse*` 模型。
- 管理后台：移除编辑抽屉内 `#aiParseSection`（开始 AI 解析、建议面板、应用建议）；移除工具栏「AI 补全」按钮（`#aiMenuBtn`）；清理 `admin.js` 中相关状态、函数与事件监听。
- 清理 `admin-studio.css`、`styles.css` 中 `.adm-ai-*`、`.ai-parse-*` 等样式。
- 将歌曲管理页统计卡片文案「近期任务 · AI 补全元数据」改为「元数据完整度」（逻辑不变，仍为本地计算的完整度百分比）。
- 更新 `openspec/specs/external-integrations`：移除全部 Dify/工作流相关要求；Purpose 改为说明当前无出站工作流集成（对象存储仍由其它规范描述）。
- 更新 `iterations/` 产品/技术文档中对 Dify 的表述（删除或改为历史说明）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `external-integrations`：移除第三方工作流（Dify）元数据 AI 解析的全部要求；更新规范 Purpose。

## Impact

- **后端**：`app/main.py`、`app/config.py`、`app/dify_workflow.py`（删除）、`app/schemas.py`
- **前端**：`app/static/admin.html`、`admin.js`、`admin-studio.css`、`styles.css`
- **配置**：`.env.example`；已部署环境可保留无用 `DIFY_*` 变量，无运行时影响
- **不受影响**：歌词 LRC、前台/后台播放、扫描入库、合并歌曲、对象存储、其它 admin API
