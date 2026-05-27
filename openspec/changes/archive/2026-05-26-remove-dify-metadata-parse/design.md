## Context

- Dify 集成：`app/dify_workflow.py`（blocking workflow + `normalize_suggestions`）、`main.py` 两个 admin 路由、`config` 四项环境变量。
- 管理端 UI：编辑抽屉 `#aiParseSection`、工具栏 `#aiMenuBtn`；`admin.js` 约 300 行（`loadAiParseEnabled`、`runAiMetadataParse`、`applyAiSuggestion*`、`renderAiSuggestPanel` 等）。
- 规范：`openspec/specs/external-integrations/spec.md` 几乎全部描述该能力。
- 统计卡片「AI 补全元数据」仅为本地元数据完整度，不调用 Dify，但文案易误解，一并改名。

## Goals / Non-Goals

**Goals:**

- 彻底移除 Dify 工作流与所有管理端 AI 解析入口。
- 删除死代码、配置与 API；后台初始化不再请求已删除的 enabled 接口。
- 规范与迭代文档与实现一致。

**Non-Goals:**

- 不替换为 OpenAI/本地 LLM 或其它供应商。
- 不删除前台歌单「AI 生成」类占位 Toast（与 Dify 无关）。
- 不改动元数据编辑抽屉的其它字段、保存逻辑与音频文件管理。

## Decisions

### 1. 硬删除而非特性开关

**选择**：删除文件、路由与 UI，不设 `ENABLE_DIFY` 类开关。

**理由**：无保留价值；开关会留下维护负担与误导性 spec。

### 2. `external-integrations` 规范处理

**选择**：delta spec 中 **REMOVED** 全部 6 条工作流相关要求；归档同步时 **MODIFIED Purpose** 为「当前无出站 HTTP 工作流集成；对象存储见其它规范」。

**理由**：该 capability 名可保留作未来其它出站集成的占位，避免重命名目录。

**备选**：删除整个 `openspec/specs/external-integrations/` —— 若团队希望零空壳，可在归档时另议。

### 3. 统计卡片改名

**选择**：标签改为「元数据完整度」；保留 `statAiTaskPct` / `statAiTaskBar` 元素 id（减少 JS 改动），仅改可见文案。

### 4. 删除顺序

1. 前端 UI + JS（避免用户点击 404）
2. API 路由 + schemas + config
3. `dify_workflow.py`
4. 样式与文档

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 用户依赖 AI 补全元数据 | 发布说明中注明移除；手工编辑与扫描标签仍可用 |
| 书签/脚本仍调用旧 API | 返回 404；无兼容层 |
| `.env` 残留 DIFY 变量 | 无害，文档中删除说明 |

## Migration Plan

1. 合并代码并部署；从 `.env` 移除 `DIFY_*`（可选）。
2. 无需数据库迁移。
3. 回滚：恢复 git 版本即可。

## Open Questions

- 无。若未来需要 AI 辅助，应新开 change 并重新设计 API/UI，不复用已删端点。
