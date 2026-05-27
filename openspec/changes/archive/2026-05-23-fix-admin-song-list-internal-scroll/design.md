## Context

歌曲管理页已采用 `admin-studio.css` 的 flex 满高布局：`adm-workspace` → `adm-main-column` → `.adm-table-scroll` + `.adm-table-footer`。`.adm-table-scroll` 已设 `overflow: auto`，表格 `min-width: 1320px`，勾选列与操作列有 sticky 冻结。

仍存在问题：

1. **`display: contents` 破坏滚动约束**：`#admin-page-music .admin-table-panel { display: contents }` 使带 `admin-table-panel` 类的 `.adm-table-scroll` 不再参与 flex 布局，可能导致 `flex: 1; min-height: 0` 失效，列表区高度不受限、滚动落到页面级。
2. **旧样式冲突**：`styles.css` 中 `#admin-page-music .admin-table-wrap` 等规则面向旧 DOM；新结构使用 `.adm-table-scroll`，部分 overflow / sticky 规则可能未生效或互相覆盖。
3. **表头未 sticky**：纵向滚动时表头随内容滚出视口，对照列名不便。
4. **滚动条不明显**：部分浏览器默认滚动条较细或 overlay 模式，用户误以为列被永久裁切。

## Goals / Non-Goals

**Goals:**

- 列表区域（`.adm-table-scroll`）在标准桌面视口下形成唯一的数据滚动容器，同时支持纵、横向滚动。
- 用户可浏览当前页全部行与全部列；表头在纵滚时保持可见。
- 表底分页栏固定于列表区底部，不随表格内容滚动。
- 溢出时出现可感知、可操作的滚动条。

**Non-Goals:**

- 虚拟滚动、无限加载或改变分页策略。
- 列显示/隐藏配置、响应式折叠列。
- 修改 sticky 列策略（保留现有勾选列左冻结、操作列右冻结）。

## Decisions

### 1. 恢复滚动容器的 flex 参与

**选择**：移除或覆盖 `#admin-page-music .admin-table-panel { display: contents }` 对歌曲列表滚动容器的生效；对 `.adm-table-scroll.admin-table-panel` 显式保留 `display: flex; flex-direction: column; flex: 1; min-height: 0; overflow: auto`（或等价的 block + overflow）。

**备选**：将 `admin-table-panel` 类从 `.adm-table-scroll` 上移除，仅保留语义类名。

**理由**：`display: contents` 会使子元素「穿透」到 `adm-main-column`，丢失独立滚动边界。

### 2. 双轴 overflow 与表格最小宽度

**选择**：`.adm-table-scroll` 使用 `overflow: auto`（同时启用 x/y）；`.adm-songs-table` 保持 `min-width`（≥ 各列 min-width 之和，当前约 1320px），`width: max-content` 或 `width: 100%` 取较大者，确保列总宽超出容器时出现横向滚动条。

**理由**：`overflow-x: hidden` 会导致中间列不可达；仅 `width: 100%` 无 min-width 会压缩列宽。

### 3. 表头 sticky

**选择**：为 `#admin-page-music .adm-songs-table thead th` 设置 `position: sticky; top: 0; z-index`（勾选列、操作列在 thead 上叠加更高 z-index），背景色与 `background-clip: padding-box` 与现有 sticky 列一致。

**理由**：纵滚时保持列标题可见，符合数据表格惯例。

### 4. 隔离旧 `styles.css` 规则

**选择**：在 `admin-studio.css` 用 `body.admin-app #admin-page-music` 前缀覆盖 `#admin-page-music .admin-table-wrap` 等对 `.adm-songs-table` 不适用或冲突的规则；避免歌曲页误用 `.admin-table-wrap` 包裹。

**理由**：减少双表结构并存时的优先级战争。

### 5. 滚动条样式

**选择**：在 `.adm-table-scroll` 上添加 `scrollbar-width: thin` 与 WebKit `::-webkit-scrollbar` 细条样式（与 `.adm-stats-row` 一致），`overflow: auto` 确保两轴均按需显示。

**理由**：提升可发现性，不改变布局逻辑。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 移除 `display: contents` 后工具栏/筛选区布局变化 | 仅针对 `.adm-table-scroll`，保留 toolbar 的 `display: contents` 若仍需要 |
| thead sticky 与左右 sticky 列 z-index 层叠 | 统一 z-index 阶梯：普通 th < sticky 左右列 < sticky thead 交叉单元格 |
| 双滚动条占用空间 | 可接受；表底分页不在滚动区内 |
| Firefox / Safari sticky + border-collapse | 已使用 `border-collapse: separate`，保持现状 |

## Migration Plan

仅静态资源与 CSS；部署后硬刷新 `admin.html` 或递增脚本/样式 `?v=` 查询参数。无数据迁移。

## Open Questions

（无）
