## Context

后台歌曲管理页（`/admin`）在工具栏「更多筛选」面板内提供六个客户端快速筛选项：原唱、作词、作曲、标签、格式、语言。每项使用 `searchable-select` 组件（基于隐藏 native `<select multiple>` + 自定义触发器与可搜索 checkbox 列表），在已加载的 `state.songs` 上做客户端过滤（同维度 OR、跨维度 AND）。

当前实现存在三处问题：

1. **P0**：`populateAdminQuickFilterSelect` 在按 state 恢复 `option.selected` 后调用 `initAdminFilterMultiSelectDefault`，该函数会将所有 option 设为未选，导致 UI 勾选无法保持。
2. **P1**：`updateAdminStats()` 在每次 `renderSongs()` 末尾调用 `populateQuickFilterOptions()`，翻页、改每页条数、仅客户端过滤时也会重建全部筛选项 DOM，造成闪烁与性能浪费。
3. **P2**：`filterMultiselectNormalizeAllSelected` 在「全部 option 被选中」时等价于未筛选；当某维度仅 1 个可选项时，用户勾选即触发归一化，表现为无法选中。

相关代码集中在 `app/static/admin.js`；样式复用 `styles.css` 中的 `searchable-select-*` 与 `admin-studio.css` 中的筛选行覆盖。

## Goals / Non-Goals

**Goals:**

- 用户可在各筛选项中通过搜索 + 多选勾选/取消勾选，且勾选状态在下拉打开期间及关闭后均正确显示。
- 筛选变更后列表与触发器文案（未选显示维度名、单选显示名称、多选显示合并或计数）正确更新。
- 仅在曲库或选项来源变化时重建筛选项列表，避免纯分页/重绘导致 DOM 重置。
- 单选项维度允许有效勾选并参与过滤。

**Non-Goals:**

- 不改变服务端列表 API 或 `/admin/filter-options` 聚合接口。
- 不将快速筛选改为服务端请求参数（仍为客户端 `songsAfterQuickFilters`）。
- 不重构 `searchable-select` 为全新组件；在现有实现上修复。
- 不改动编辑面板内的 `multi-select`（艺人/语言等）行为。

## Decisions

### 1. P0：移除错误的 `initAdminFilterMultiSelectDefault` 调用

**决定**：从 `populateAdminQuickFilterSelect` 中删除对 `initAdminFilterMultiSelectDefault` 的调用；该函数仅保留在 `renderSelectOptions` 等「新建选项、初始无选中」路径。

**理由**：恢复选中与「默认全不选」语义互斥；一行删除即可修复主 bug。

**备选**：在 `initAdminFilterMultiSelectDefault` 内增加「skip if restoring」参数 —— 复杂且易再犯，不采用。

### 2. P1：拆分「刷新选项列表」与「更新统计」

**决定**：

- 从 `updateAdminStats()` 移除 `populateQuickFilterOptions()`。
- 新增 `refreshAdminMusicQuickFilterOptions()`（或直接调用 `populateQuickFilterOptions`）并在以下时机调用：
  - 初始 `loadSongs()` 完成后（可与 `updateAdminStats` 并列）；
  - 扫描/导入完成、`loadFilterOptions` 后重载歌曲时；
  - 标签/语言/艺人等影响选项来源的管理操作后（现有 `loadSongs` + `loadFilterOptions` 链路上补一次即可）。

**理由**：`populateQuickFilterOptions` 依赖 `state.songs` 与 `state.tags` 汇总值，仅在数据源变化时需要；`renderSongs` 仅做表格分页与客户端过滤展示。

**备选**：在 `populateQuickFilterOptions` 内 diff 选项避免重建 —— 过度工程；解耦调用点更简单。

### 3. P2：全选归一化增加选项数量门槛

**决定**：`filterMultiselectNormalizeAllSelected` 仅在 `selectEl.options.length > 1` 且全部选中时清空选中；单选项时保留选中。

**理由**：单选项时「全选」与「选这一项」语义相同，应允许作为有效筛选；多选项时保留「全选 = 不筛选」的产品约定，避免触发器显示「全部」但列表仍被过滤的割裂感。

**备选**：单选项时隐藏该筛选项 —— 改动 UI 结构，非必要。

### 4. 勾选后是否立即 `renderSongs`

**决定**：保持 `onQuickFilterChange` → `syncQuickFiltersFromUi` → `renderSongs`；P0 修复后不再触发错误的 repopulate。

**理由**：行为不变，仅修复状态同步。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 漏掉某条 `loadSongs` 路径未刷新选项，新增歌曲后筛选项不更新 | tasks 中枚举所有 `loadSongs` / 扫描完成调用点并补 `populateQuickFilterOptions` |
| 移除 `updateAdminStats` 内 populate 后，首次进入页面选项为空直到 load 完成 | 初始 `Promise.all` 链在 `loadSongs` 后显式 populate（已存在 `updateAdminStats` 调用，改为独立调用） |
| 单选项维度勾选后触发器显示名称而非维度名 | 与多选一致，符合预期 |

## Migration Plan

1. 修改 `admin.js`， bump `admin.html` 中脚本 query 版本。
2. 本地硬刷新 `/admin`，验证六个筛选项的多选、搜索、重置、翻页不丢状态。
3. Docker 环境若已挂载 `./app`，重启 app 容器即可；无数据库迁移。
4. 回滚：还原 `admin.js` / `admin.html` 版本号。

## Open Questions

（无 — 范围与 P0/P1/P2 已在 explore 阶段确认。）
