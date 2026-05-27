## 1. 后台编辑抽屉布局与移除草稿

- [x] 1.1 在 `admin.html` 删除 `#saveDraftBtn`（「保存草稿」）按钮
- [x] 1.2 在 `admin.js` 移除 `saveDraftBtn` 元素引用、`click` 监听器及 `localStorage` 草稿写入逻辑
- [x] 1.3 在 `admin-studio.css` 为 `.admin-edit-panel.is-open` 与 `.drawer-form` 补充全高 flex 样式（`align-self: stretch` / `height: 100%`、`flex: 1; min-height: 0`），确保 `.drawer-body-scroll` 内滚动、头尾固定

## 2. 后台歌曲列表新增影视剧列

- [x] 2.1 在 `admin.html` 表头于「语言」与「标签」之间插入「影视剧」列（`data-sort="film_tv"`）
- [x] 2.2 在 `admin.js` `renderSongs` 中于语言与标签单元格之间渲染 `song.film_tv`（空值「—」）
- [x] 2.3 将空列表 `colspan` 从 15 更新为 16；确认排序指示器对 `film_tv` 生效

## 3. 前台音乐库列表新增影视剧列

- [x] 3.1 在 `index.html` 表头于「语言」与「标签」之间插入 `<th class="sk-col-meta">影视剧</th>`
- [x] 3.2 在 `frontend.js` 行模板于 language 与 tags 单元格之间插入 `film_tv` 展示（空值「—」）
- [x] 3.3 如有空态 `colspan` 或列宽样式，同步更新

## 4. 验收与缓存

- [x] 4.1 手动验证：打开编辑抽屉面板与表格同高、长表单正文可滚动、底部仅「取消」「保存」
- [x] 4.2 手动验证：后台/前台列表「影视剧」列位于「标签」前，有值正确展示、无值显示「—」；后台影视剧列排序请求含 `sort_by=film_tv`
- [x] 4.3 递增 `admin.html` / `index.html` 中静态资源 `?v=` 缓存参数
