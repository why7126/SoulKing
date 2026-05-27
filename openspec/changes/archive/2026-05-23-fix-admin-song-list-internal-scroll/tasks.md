## 1. 滚动容器布局修复

- [x] 1.1 在 `admin-studio.css` 中覆盖 `#admin-page-music .adm-table-scroll.admin-table-panel`：移除 `display: contents` 影响，显式设置 `flex: 1; min-height: 0; overflow: auto`（双轴）
- [x] 1.2 确认 `adm-main-column` → `.adm-table-scroll` → `.adm-table-footer` 的 flex 列链完整，表底 `flex-shrink: 0` 且不参与表格滚动
- [x] 1.3 检查并覆盖 `styles.css` 中 `#admin-page-music .admin-table-wrap` 等对 `.adm-songs-table` 不适用或冲突的 overflow 规则

## 2. 表格双轴滚动与列宽

- [x] 2.1 确保 `.adm-songs-table` 保持足够 `min-width`（≥ 各列之和），使列总宽超出容器时出现横向滚动条
- [x] 2.2 验证横向滚动可访问中间列（发行日期、元数据、创建/更新时间）；操作列 sticky 与横向滚动行为不冲突
- [x] 2.3 在 `.adm-table-scroll` 添加细滚动条样式（`scrollbar-width: thin` 与 WebKit scrollbar），提升滚动条可发现性

## 3. 表头 sticky

- [x] 3.1 为 `#admin-page-music .adm-songs-table thead th` 添加 `position: sticky; top: 0` 与背景色
- [x] 3.2 调整 thead sticky 与勾选列（left）、操作列（right）sticky 的 z-index 层叠，避免交叉单元格被遮挡

## 4. 验收

- [x] 4.1 标准桌面视口（如 1440×900）：页面无纵/横滚动条，列表容器内可纵滚当前页全部行、横滚全部列
- [x] 4.2 纵滚时表头固定可见；表底分页栏始终固定在列表区底部
- [x] 4.3 每页 50/100 条、列宽溢出场景下手动验证双轴滚动与 sticky 列表现
