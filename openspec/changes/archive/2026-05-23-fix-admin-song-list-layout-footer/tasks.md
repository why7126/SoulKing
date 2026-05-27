## 1. 滚动与 body 样式

- [x] 1.1 `body.admin-app` / `body.admin-table-body`：清零 `padding-bottom`，避免撑出页面纵滚
- [x] 1.2 确保 `.admin-app .app-admin-main-wrap` 为 `overflow: hidden` + flex 子项 `min-height: 0`，覆盖 `styles.css` 中 `.app-admin-main-wrap { overflow-y: auto }`
- [x] 1.3 确认 `.admin-app .admin-main` / `.admin-studio-root` / `.adm-main-column` 链路上无 `overflow: visible` 导致撑高

## 2. 表底栏结构

- [x] 2.1 `admin.html`：移除 `adm-batch-bar`；footer 左 `#songListTotalLabel`、右 `.adm-pagination`（翻页 + 每页条数）
- [x] 2.2 `admin-studio.css`：`.adm-table-footer` 单行 `space-between`；`.adm-list-total` 左对齐、无多余 `margin-right` 挤到中间
- [x] 2.3 `admin.js`：移除表底 batch 相关 `els` 与 `updateBatchButtons` 中对表底按钮的引用（保留顶栏批量逻辑）

## 3. 操作列与表格横向

- [x] 3.1 歌曲表 `border-collapse: separate`（与 sticky 兼容）
- [x] 3.2 `col-actions`：`sticky right: 0`、背景/z-index、`min-width` ≥ 148px；`.adm-actions-cell` 不换行
- [x] 3.3 视情况为 `col-check` 保留左侧 sticky；检查 `updated_at` 列在滚到右侧时可见

## 4. 分页展示

- [x] 4.1 确认 `renderPagination` / `loadSongs` 在无筛选、有数据时仍渲染页码与「共 N 首」
- [x] 4.2 递增 `admin.html` / `admin-studio.css` 的 `?v=` 缓存版本

## 5. 验收

- [x] 5.1 手动验收：无页面纵滚、表底左「共 N 首」右分页、无表底批量按钮、更新时间/操作列可见、未筛选时有分页
