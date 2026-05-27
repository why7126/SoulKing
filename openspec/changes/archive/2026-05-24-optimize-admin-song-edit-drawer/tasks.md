## 1. 布局与样式

- [x] 1.1 将 `admin-studio.css` 中 `--adm-edit-w` 从 `380px` 调整为 `480px`（或设计文档约定范围），确认窄屏 `min(100vw, …)` 仍正常
- [x] 1.2 在 `admin.html` 抽屉表单中：「艺人」改为「原唱」；作词/作曲移出 `adm-hidden-filters`；新增 `.adm-form-grid-3` 容纳原唱/作词/作曲；移除 `#editFormatDisplay` 表单项
- [x] 1.3 在音频文件区块增加只读格式展示容器（如 `#editFormatsReadonly`），样式为 chip/标签列表

## 2. 标签多选组件

- [x] 2.1 将 `#singleTagOptions` 改为 `multi-select` 容器（如 `#tagInput`），更新 `admin.js` 中 `els` 引用
- [x] 2.2 实现 `renderTagMultiSelect(selectedIds)`，对齐 `renderLanguageMultiSelect`（模糊搜索、多选、POST `/tags` 新建、最近使用 localStorage）
- [x] 2.3 `loadTags` / `openEditModal` / 保存元数据流程改为使用 `getSelectedTagIds()`（或等价）提交 `tag_ids`；删除或废弃 `renderTagOptions`

## 3. 艺人字段与格式聚合

- [x] 3.1 确认 `openEditModal` 对 `leadArtistInput`（歌手）、`lyricistInput`（作词）、`composerInput`（作曲）均调用 `renderArtistMultiSelect` 且标签文案正确
- [x] 3.2 实现 `formatsFromDetailFiles(files)` 并在 `openEditModal`、添加/删除音频文件回调中刷新 `#editFormatsReadonly`
- [x] 3.3 移除对 `els.editFormatDisplay` 的读写；保存/草稿逻辑不包含格式字段

## 4. 验收与缓存

- [x] 4.1 手动验证：三艺人字段搜索/多选/新建；标签搜索/多选/新建；多格式只读展示随文件变更更新；抽屉宽度足够
- [x] 4.2 递增 `admin.html` 引用的 `admin.js` / `admin-studio.css` 的 `?v=` 缓存参数
