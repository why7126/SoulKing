## 1. 样式基础

- [x] 1.1 在 `admin-studio.css` 抽取或新增 `.adm-data-table`（与 `.adm-songs-table` 共享表头/行/空单元格样式）
- [x] 1.2 合并 `.manager-sort-btn` 与 `.sort-btn` 的 Admin 表头排序样式
- [x] 1.3 定义 Admin 批量危险操作按钮样式（`btn-adm-ghost` + 危险色），供批量删除使用

## 2. HTML 结构（admin.html）

- [x] 2.1 将「艺人管理」改为 `admin-studio-root` + `adm-toolbar` + `adm-search-wrap` + `adm-table-scroll` + `adm-table-footer` 结构
- [x] 2.2 将「标签管理」改为同上 Admin 结构
- [x] 2.3 将「语言管理」改为同上 Admin 结构
- [x] 2.4 将「用户管理」改为同上 Admin 结构，并增加用户搜索输入与底栏占位元素
- [x] 2.5 移除四页页头内联 `style`，删除冗余 `panel` / `admin-table-layout` 双层包裹

## 3. 脚本逻辑（admin.js）

- [x] 3.1 更新 `els` 与事件绑定以匹配新 DOM id/结构（搜索清空、批量删除按钮类名）
- [x] 3.2 为艺人/标签/语言列表实现客户端分页与 `adm-list-total` / `adm-pagination` 更新
- [x] 3.3 实现用户管理搜索过滤（用户名、昵称子串）
- [x] 3.4 确认全选 checkbox 与分页行为与歌曲列表一致（或按 spec 文档化当前页范围）
- [x] 3.5 将行内渲染模板中的批量删除按钮触发逻辑与新的 `hidden` / 类名兼容

## 4. 文档与验收

- [x] 4.1 更新 `ui-design.md` 后台 Admin 节：参考数据管理页布局与组件对照表
- [x] 4.2 手动验收：艺人/标签/语言/用户四页搜索、新建、编辑、删除、批量删除、排序、分页
- [x] 4.3 回归：歌曲管理页工具栏、表格、播放器与编辑抽屉未受影响

## 5. 操作列「更多」菜单（后续对齐）

- [x] 5.1 抽取 `managerRowActionsCell` / `wireTableMoreMenuOnRow`，歌曲列表复用同一套逻辑
- [x] 5.2 艺人/标签/语言/用户四页操作列改为仅 ⋮，菜单内承载原行内操作
- [x] 5.3 `adm-data-table` 操作列 sticky 底色与 `table-more-menu` Admin 样式
- [x] 5.4 表头操作列增加 `col-actions` class
