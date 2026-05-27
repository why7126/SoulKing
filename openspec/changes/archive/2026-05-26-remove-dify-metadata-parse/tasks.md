## 1. 管理后台 UI 与脚本

- [x] 1.1 `admin.html`：删除 `#aiParseSection` 整块与工具栏 `#aiMenuBtn`
- [x] 1.2 `admin.html`：统计卡片标签改为「元数据完整度」
- [x] 1.3 `admin.js`：删除 `aiParseEnabled`、`aiSuggestions` 及所有 `ai*` 解析/应用函数与事件绑定
- [x] 1.4 `admin.js`：从初始化 `Promise.all` 移除 `loadAiParseEnabled()`
- [x] 1.5 `admin.js`：清理 `openEditModal` / `closeEditModal` 中对 AI 面板的引用
- [x] 1.6 `admin-studio.css`、`styles.css`：删除 `.adm-ai-*`、`.ai-parse-*`、`.ai-suggest-*` 等仅用于 Dify 的样式

## 2. 后端 API 与配置

- [x] 2.1 删除 `app/dify_workflow.py`
- [x] 2.2 `main.py`：删除两个 ai-parse 路由及 `dify_workflow` / 相关 schema 导入
- [x] 2.3 `schemas.py`：删除 `SongMetadataAiParseIn/Out/EnabledOut`
- [x] 2.4 `config.py`、`.env.example`：删除全部 `dify_workflow_*` / `DIFY_*` 配置项

## 3. 文档与验收

- [x] 3.1 更新 `iterations/产品设计方案.md`、`iterations/技术实现方案.md` 中 Dify 相关段落
- [x] 3.2 验收：后台编辑抽屉无 AI 解析区；工具栏无「AI 补全」；`POST /admin/song-metadata/ai-parse` 返回 404；保存元数据/歌词上传/扫描仍正常
