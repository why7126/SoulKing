## 1. 操作列行内 sticky（P0）

- [x] 1.1 `admin.js`：歌曲行 `td.col-actions` 内增加 `<div class="adm-actions-inner">` 包裹四个操作按钮，移除 `td` 上的 `adm-actions-cell` class
- [x] 1.2 `admin-studio.css`：将 `.adm-actions-cell { display: flex }` 改为 `.adm-actions-inner { display: flex; align-items: center; gap: 4px; flex-wrap: nowrap; white-space: nowrap }`；确认 `td.col-actions` 无 `display` 覆盖
- [x] 1.3 确认 `tbody td.col-actions` 保留 `position: sticky; right: 0`、背景与 z-index；必要时用 `body.admin-app #admin-page-music` 前缀覆盖 `styles.css` 中 `tbody td { position: relative }` 对操作列的影响
- [x] 1.4 手动验收：表格横滚到中间位置时，多行编辑/播放/下载/更多仍贴在容器右缘且可点

## 2. 快速筛选多选（P0 / P1 / P2）回归

- [x] 2.1 确认 `populateAdminQuickFilterSelect` 在恢复选中后**不**调用 `initAdminFilterMultiSelectDefault`
- [x] 2.2 确认 `filterMultiselectNormalizeAllSelected` 仅在 `options.length > 1` 且全选时清空
- [x] 2.3 确认 `updateAdminStats` / `renderSongs` **不**调用 `populateQuickFilterOptions`；`loadSongs` 与 `loadPeople`/`loadTags`/`loadLanguages` 完成后会刷新
- [x] 2.4 手动验收：勾选保持、翻页/改每页条数不丢选、单选项维度可筛、重置有效

## 3. 筛选项选项来源回归

- [x] 3.1 确认 `populateQuickFilterOptions` 使用 `catalogPeopleNamesByType`（歌手/作词/作曲）、`state.tags`、`state.languages`；格式仍从 `state.filters.formats` 推导
- [x] 3.2 手动验收：曲库中无歌曲的标签/语言仍出现在下拉；原唱/作词/作曲按艺人类型区分

## 4. 列表滚动与表底布局回归

- [x] 4.1 确认 `.adm-table-scroll.admin-table-panel` 参与 flex 且 `overflow: auto`；无 `display: contents` 破坏高度约束
- [x] 4.2 确认 `thead th` 纵滚 sticky；表底左「共 N 首」、右分页；无表底批量区
- [x] 4.3 手动验收：无页面级纵/横滚；容器内双轴滚动可访问全部列与行；表底分页始终可见

## 5. 收尾

- [x] 5.1 递增 `admin.html` 中 `admin.js`、`admin-studio.css` 的 `?v=` 缓存版本
- [x] 5.2 完整回归：筛选 + 横滚操作列 + 分页 + 顶栏批量（表底无批量）
