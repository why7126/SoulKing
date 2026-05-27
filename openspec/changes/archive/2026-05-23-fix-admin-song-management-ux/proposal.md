## Why

后台歌曲管理页在近期多轮迭代（多选筛选、参考数据选项来源、列表列与分页、表底布局、双轴滚动）后，仍存在影响日常使用的缺口：筛选项多选勾选无法保持、选项来源与参考数据不一致、列表区域滚动边界不稳定，以及**操作列仅表头冻结、行内按钮随横向滚动消失**。需要在一轮变更中对照既有规范补齐实现与验收，并修复操作列 tbody sticky 失效的根因。

## What Changes

- **P0 — 多选勾选持久化**：`populateAdminQuickFilterSelect` 恢复选中后不得再调用 `initAdminFilterMultiSelectDefault` 清空；勾选/取消与触发器文案同步。
- **P1 — 筛选项刷新解耦**：`populateQuickFilterOptions` 不在每次 `renderSongs` / `updateAdminStats` 中调用；仅在曲库重载、扫描完成、艺人/标签/语言参考数据变更后刷新；翻页/改每页条数时保留已选。
- **P2 — 单选项维度归一化**：`filterMultiselectNormalizeAllSelected` 仅在 `options.length > 1` 且全选时等价于「未筛选」；单选项维度可保持勾选并生效。
- **筛选项召回来源**：原唱/作词/作曲取自艺人管理并按 `types` 过滤；标签、语言取自标签/语言管理列表；格式仍从曲库推导；已选值在新选项列表中仍存在时保留。
- **列表双轴滚动**：纵向与横向滚动仅发生在 `.adm-table-scroll`；表头纵滚 sticky；表底分页在滚动容器外；避免 `display: contents` 破坏 flex 高度约束。
- **操作列行内冻结（新增修复）**：横向滚动时 `tbody td.col-actions` 与表头一同 `sticky right: 0`；**禁止**对操作列 `<td>` 使用 `display: flex`（改由内层包裹元素承担 flex 布局），避免破坏 `table-cell` 导致行内 sticky 失效。
- **列表布局收尾**：表底左「共 N 首」、右分页；无表底批量区；操作列宽度足以容纳编辑/播放/下载/更多。
- 递增 `admin.html` / `admin.js` / `admin-studio.css` 静态资源 `?v=`。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：强化歌曲管理页快速筛选多选交互、选项来源、列表容器双轴滚动、操作列行内 sticky 与验收场景。

## Impact

- **前端**：`app/static/admin.js`（筛选 populate/多选逻辑、歌曲行模板）、`app/static/admin-studio.css`（操作列 sticky、`.adm-actions-inner`、滚动容器）、`app/static/admin.html`（必要时行模板结构、缓存版本）。
- **样式冲突**：`styles.css` 中 `#admin-page-music .admin-table` 旧规则与 `admin-studio.css` 并存，需以后台专用选择器收敛。
- **后端 / API**：无变更（筛选仍走现有 `/songs` 查询参数与 `/people`、`/tags`、`/languages`）。
