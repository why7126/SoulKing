## 1. 筛选项数据源改造

- [x] 1.1 在 `populateQuickFilterOptions` 中，原唱选项改为 `peopleByType("歌手")` 的名称列表（`zh-CN` 升序）
- [x] 1.2 作词选项改为 `peopleByType("作词")` 的名称列表
- [x] 1.3 作曲选项改为 `peopleByType("作曲")` 的名称列表
- [x] 1.4 标签选项改为仅 `state.tags` 的 `name`，移除从歌曲 `tags` 合并的逻辑
- [x] 1.5 语言选项改为 `state.languages` 的 `name`，移除从歌曲 `language` 推导的逻辑
- [x] 1.6 确认格式维度仍从曲库文件格式推导，行为不变

## 2. 刷新时机与已选保留

- [x] 2.1 确认 `loadPeople` / `loadTags` / `loadLanguages` 及 CRUD 成功后的调用链会触发 `populateQuickFilterOptions`
- [x] 2.2 验证 `populateAdminQuickFilterSelect` 在选项重建后仍保留存在于新列表中的已选值

## 3. 发布与验收

- [x] 3.1 更新 `admin.html` 中 `admin.js` 的 `?v=` 缓存版本号
- [x] 3.2 手动验收：管理页新增歌手/作词/作曲/标签/语言后筛选项出现；勾选后列表 OR/AND 过滤正确；翻页不丢失选中；格式筛选不受影响
