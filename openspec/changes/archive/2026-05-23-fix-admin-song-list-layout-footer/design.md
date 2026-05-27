## Context

歌曲管理页采用 `admin-studio.css` 的 flex 满高布局（`app-shell` → `adm-workspace` → `adm-table-scroll` + `adm-table-footer`），但与 `styles.css` 中前台/旧后台规则并存：`body` 全局 `padding-bottom: 120px`、`body.admin-body.admin-table-body` 清零规则未覆盖 `body.admin-app`；`.app-admin-main-wrap` 在 `styles.css` 中仍为 `overflow-y: auto`。表底使用 `justify-content: space-between`，左侧 `adm-batch-bar` 与右侧 `adm-pagination`（内含「共 N 首」）分列。操作列在 `styles.css` 中 `min-width: 84px`，当前主操作含编辑/播放/下载/更多共四个控件，宽表下右侧列易被裁切。

## Goals / Non-Goals

**Goals:**

- 视口内无整页纵向滚动条（仅表格 `.adm-table-scroll` 可纵/横向滚动）。
- 表底：左「共 N 首」、右分页控件；无表底批量按钮区。
- 操作列、更新时间在横向滚动时仍可见（右侧 sticky + 足够列宽）。
- 有数据时表底分页控件始终渲染且位于列表区底部可见区域。

**Non-Goals:**

- 列显示/隐藏配置、响应式隐藏次要列。
- 修改顶部工具栏批量能力。
- 将删除从「更多」菜单移到主操作区（保持现有 spec：删除可在更多菜单）。

## Decisions

### 1. 滚动容器归一

**选择**：`body.admin-app`（及 `body.admin-table-body`）设置 `padding-bottom: 0`、`overflow: hidden`（或 `min-height: 100vh` 且不撑高）；`.admin-app .app-admin-main-wrap` 明确 `overflow: hidden; flex: 1; min-height: 0`；覆盖或移除 `styles.css` 中 `.app-admin-main-wrap { overflow-y: auto }` 对后台的生效（提高选择器优先级或加 `body.admin-app` 前缀）。

**理由**：避免双滚动条、表底被滚出视口。

### 2. 表底 DOM 与布局

**选择**：从 `admin.html` 移除 `adm-batch-bar` 整块；`adm-table-footer` 改为单行 flex：`justify-content: space-between; align-items: center`，子元素为 `#songListTotalLabel`（左）与 `.adm-pagination`（右，仅含翻页与每页条数）。

**理由**：满足左对齐总数、去掉重复批量入口。

**JS**：`updateBatchButtons` 保留对顶部工具栏按钮的控制；移除或不再引用表底 batch 相关 `els`。

### 3. 操作列 sticky 与列宽

**选择**：在 `admin-studio.css`（或统一在 `#admin-page-music`）为 `.adm-songs-table` 使用 `border-collapse: separate`（与 `styles.css` 冻结列规则一致）；`th.col-actions, td.col-actions` 设置 `position: sticky; right: 0; z-index` 与背景色；`min-width` 提升至约 148–160px。可选：勾选列 `left: 0` sticky 保留。

**理由**：列增多后用户无需滚到最右才能操作。

### 4. 分页可见性

**选择**：不新增「仅多页时显示分页」逻辑；`renderPagination` 在 `total >= 0` 时始终更新页码与禁用态；确保 `loadSongs` 成功后 footer 不被 `hidden` 或 `display:none`。

**理由**：用户要求未筛选时也看到分页；单页时仍显示「共 N 首」与页码 `1`。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| `styles.css` 与 `admin-studio.css` 优先级冲突 | 以后台专用选择器 `body.admin-app #admin-page-music` 收敛 |
| 移除表底批量后用户习惯变化 | 顶部工具栏已有同等能力 |
| sticky 与 `border-collapse: collapse` 冲突 | 歌曲表统一 `separate` |

## Migration Plan

仅静态资源与 CSS；部署后硬刷新 `admin.html` / 递增 `?v=`。

## Open Questions

（无）
