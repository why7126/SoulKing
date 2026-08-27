## Why

后台歌曲管理页的「编辑歌曲」右侧抽屉是日常维护元数据的主入口，但当前表单与列表列语义不一致：艺人仍合并为单一「艺人」字段，作词/作曲被隐藏在 `adm-hidden-filters` 中；标签仍使用平铺复选框，无法模糊搜索与快速新建；抽屉宽度（`--adm-edit-w: 380px`）偏窄；格式字段以只读输入框展示且仅反映单个文件，与「一曲多格式」的数据模型不符。需要统一为与「语言」字段相同的多选交互范式，并加宽抽屉、由音频文件自动推导格式展示。

## What Changes

- **艺人字段拆分与统一交互**：移除单一「艺人」标签；在抽屉主表单中并列展示 **原唱**、**作词**、**作曲** 三个字段，均使用与 `languageInput` 相同的多选组件模式（模糊搜索、多选勾选、搜索框内输入新建、最近使用排序、触发器 chip 展示）。
- **标签字段升级**：将 `singleTagOptions` 平铺复选框改为与语言一致的多选下拉（`multi-select`），支持模糊搜索、多选、输入新建标签（调用现有 `/tags` API）。
- **抽屉加宽**：增大 `--adm-edit-w`（及移动端 `min(100vw, …)` 上限），为三列艺人 + 标签多选留出足够空间。
- **格式只读且自动关联**：从抽屉表单中 **移除可编辑的格式输入**；格式由该曲关联的 **全部音频文件** 的 `format` 聚合展示（如 WAV、FLAC、APE、MP3，去重、大写）；添加/删除/重命名音频文件后同步刷新展示；保存元数据时 **不再** 由用户编辑格式字段。
- **隐藏字段整理**：作词、作曲移出 `adm-hidden-filters`；影视剧、风格等仍可按现有策略保留在折叠/隐藏区（本变更不扩展影视剧/风格需求，除非实现时已无独立入口）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充后台歌曲管理页编辑抽屉的字段布局、原唱/作词/作曲与标签的多选交互、抽屉宽度、格式只读聚合展示等需求与验收场景。

## Impact

- **前端**：`app/static/admin.html`（抽屉表单结构、移除格式输入、标签容器改为 `multi-select`）、`app/static/admin.js`（复用/抽取 `renderLanguageMultiSelect` 模式实现 `renderTagMultiSelect`；原唱/作词/作曲标签与可见性；`openEditModal` 格式展示逻辑；保存草稿/提交时 tag_ids 与 lead/lyricist/composer ids）、`app/static/admin-studio.css`（`--adm-edit-w`、表单栅格、`.adm-hidden-filters` 调整）。
- **后端 / API**：无契约变更（仍使用现有 `/people`、`/tags`、`/languages` 与歌曲详情 `files[].format`、`formats`）；可选在前端统一从 `detail.files` 推导展示，不新增端点。
- **规范对齐**：与列表列（原唱、作词、作曲、标签、格式）及前台筛选多选模式保持一致。
