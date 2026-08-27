## Context

歌曲管理页（`admin.html` + `admin.js` + `admin-studio.css`）已完成多轮改造：服务端分页、14 列数据表、参考数据驱动的筛选项、`searchable-select` 多选、`.adm-table-scroll` 双轴滚动、表底单行分页、操作列 `sticky right: 0`。

仍存在的缺口：

1. **操作列行内 sticky 失效**：`td.col-actions` 与 `.adm-actions-cell` 同元素上同时设置 `position: sticky` 与 `display: flex`，导致 `<td>` 脱离 `table-cell` 布局，tbody 行在横向滚动时操作按钮随表格滚走，仅表头「操作」看似固定。
2. **筛选与列表**：部分 P0/P1/P2 与选项来源逻辑已在代码中落地，需在本变更中**回归验证**并修补遗漏调用点（若仍存在 `renderSongs` 链路上的多余 `populateQuickFilterOptions`）。
3. **样式双轨**：`styles.css` 中 `#admin-page-music .admin-table` 与 `admin-studio.css` 中 `.adm-songs-table` 规则并存，需避免 `tbody td { position: relative }` 等规则意外覆盖 sticky 列。

## Goals / Non-Goals

**Goals:**

- 横向滚动时，**每一行**操作列按钮与表头一同钉在滚动容器右侧，可点击。
- 快速筛选多选：勾选持久、翻页不丢选、单选项维度可筛、选项来源符合参考数据规范。
- 列表仅在 `.adm-table-scroll` 内纵/横滚；表头纵滚 sticky；表底分页固定可见。
- 操作列 `<td>` 保持 `table-cell`；flex 布局仅用于内层包裹元素。

**Non-Goals:**

- 恢复左侧「歌曲名 + 原唱」多列冻结（旧 `col-sticky-title` 方案）。
- 列显示/隐藏配置、虚拟滚动、SQL 层分页优化。
- 将删除从「更多」菜单移到主操作区。

## Decisions

### 1. 操作列 DOM：内层 flex 包裹

**选择**：`admin.js` 行模板改为：

```html
<td class="col-actions" data-stop-row="1">
  <div class="adm-actions-inner">…四个按钮…</div>
</td>
```

**样式**：将 `.adm-actions-cell { display: flex }` 迁移为 `.adm-actions-inner { display: flex; … }`；`td.col-actions` 不设 `display` 覆盖。

**理由**：保留 table 列宽算法与 `position: sticky` 在 tbody 上的有效性（Chromium/WebKit 实测行为）。

**备选**：`display: table-cell !important` 与 flex 并存 —— 不可靠，不采用。

### 2. sticky 与 z-index 层叠

**选择**：维持 `admin-studio.css` 现有阶梯：`tbody td.col-actions` z-index 15、`thead th.col-actions` 25；`border-collapse: separate`；`min-width: 156px`；`background-clip: padding-box`。

**理由**：与勾选列左冻结、表头 `top: 0` sticky 已调过的层叠一致。

### 3. 筛选 populate 调用链审计

**选择**：确认 `populateAdminQuickFilterSelect` 不调用 `initAdminFilterMultiSelectDefault`；`updateAdminStats` / `renderSongs` 不调用 `populateQuickFilterOptions`；在 `loadSongs` 成功、`loadPeople`/`loadTags`/`loadLanguages` 完成后调用。

**理由**：对齐已归档的 P0/P1 与选项来源变更；本变更以审计 + 补缺为主。

### 4. 滚动容器

**选择**：保持 `.adm-table-scroll.admin-table-panel { display: flex; flex: 1; min-height: 0; overflow: auto }`，禁止对滚动容器使用 `display: contents`。

**理由**：避免整页滚动与表底被滚出视口。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 内层 div 增加 DOM 深度 | 仅操作列一行，影响可忽略 |
| `styles.css` 旧规则覆盖 sticky | 用 `body.admin-app #admin-page-music .adm-songs-table tbody td.col-actions` 显式声明 sticky |
| 误以为其它列也应右冻结 | 范围仅限 `col-actions`；「更新时间」通过横滚访问（spec 已有场景） |

## Migration Plan

1. 部署静态资源（递增 `?v=`），无需数据库迁移。
2. 硬刷新后台页，按 tasks 验收清单手动回归筛选与横滚。

## Open Questions

（无）
