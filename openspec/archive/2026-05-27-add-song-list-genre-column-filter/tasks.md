## 1. 后端

- [x] 1.1 在 `app/main.py` 的 `list_songs` 排序映射中增加 `"genre": item.genre or ""`，使 `sort_by=genre` 生效

## 2. 后台歌曲列表与筛选

- [x] 2.1 在 `admin.html` 表头「语言」后增加「风格」列（`data-sort="genre"`）；`adm-filters-panel` 在 `filterLanguageQuick` 后增加 `filterGenreQuick` 多选
- [x] 2.2 在 `admin.js` 注册 `filterGenreQuick`、`quickFilterGenres` 状态；实现 `quickFilterGenreIds()` 与 `buildSongListQueryParams` 中 `genre_ids` 追加
- [x] 2.3 在 `populateQuickFilterOptions` 用 `state.genres` 填充风格筛选项；`loadGenres` 完成后刷新；重置筛选时清空风格
- [x] 2.4 在 `renderSongs` 语言列后输出 `song.genre`；空列表 `colspan` 与排序按钮同步更新

## 3. 后台编辑抽屉

- [x] 3.1 将 `admin.html` 中 `#genreInput` 移出 `adm-hidden-filters`，与「语言」并列于 `adm-form-grid-2` 可见区
- [x] 3.2 确认 `openEditModal` / 保存流程已绑定 `renderGenreMultiSelect` 与 `genre_ids`（无回归即可勾选完成）

## 4. 前台音乐库

- [x] 4.1 在 `index.html` 表头「语言」后增加「风格」列；筛选面板在 `languageSelect` 后增加 `genreSelect`
- [x] 4.2 在 `frontend.js` 增加 `genreSelect`、风格筛选状态、选项填充（`/genres` 或 `state.filters.genres`）、查询参数 `genre_ids` 映射
- [x] 4.3 在列表行渲染中语言列后输出 `song.genre`；重置筛选与「更多筛选」七维文案/顺序与后台对齐

## 5. 验证

- [x] 5.1 手动验证：后台/前台列表风格列展示、风格筛选（含多选 OR）、风格列排序、编辑抽屉风格可见且可保存回显
