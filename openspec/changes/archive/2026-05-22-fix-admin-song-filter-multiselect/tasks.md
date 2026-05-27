## 1. P0 — 修复勾选状态被清空

- [x] 1.1 在 `app/static/admin.js` 的 `populateAdminQuickFilterSelect` 中移除对 `initAdminFilterMultiSelectDefault` 的调用（保留 `renderSelectOptions` 等初始路径中的用法）
- [x] 1.2 本地验证：展开任一筛选项，勾选 1～2 项后 checkbox 与触发器文案保持正确

## 2. P2 — 单选项维度全选归一化

- [x] 2.1 修改 `filterMultiselectNormalizeAllSelected`：仅当 `options.length > 1` 且全部选中时才清空选中
- [x] 2.2 验证：某维度仅 1 个可选项时勾选后保持选中且列表被过滤

## 3. P1 — 解耦选项刷新与列表重绘

- [x] 3.1 从 `updateAdminStats()` 中移除 `populateQuickFilterOptions()` 调用
- [x] 3.2 在 `loadSongs()` 成功加载后调用 `populateQuickFilterOptions()`（在 `renderSongs` 之前或之后，确保 state 已更新）
- [x] 3.3 确认扫描完成、批量导入/删除后重载歌曲等路径仍会刷新选项（在现有 `loadSongs` / `Promise.all([loadFilterOptions(), loadSongs()])` 链路上补调用，避免遗漏）
- [x] 3.4 调整初始 `Promise.all([... loadSongs()]).then(() => updateAdminStats())`：在 `loadSongs` 内或 then 中显式 populate，保证首屏选项可用
- [x] 3.5 验证：已选筛选条件下翻页、改每页条数，勾选状态与触发器不变；扫描或重载歌曲后选项列表更新且合法已选值保留

## 4. 收尾

- [x] 4.1 bump `app/static/admin.html` 中 `admin.js` 查询版本号
- [x] 4.2 手动回归：六个维度搜索 + 多选、重置按钮、跨维度 AND 过滤、「更多筛选」展开/收起
