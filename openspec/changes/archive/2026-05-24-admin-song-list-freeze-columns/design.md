## Context

后台歌曲管理表格（`.adm-songs-table`）已具备 `border-collapse: separate`、左侧 `col-check` 与右侧 `col-actions` 的 sticky，以及 tbody `isolation: isolate` 与中间列 `z-index: 0`。但「歌曲」列（表头第 2 列、数据行第 2 个 `<td>`）未标记 sticky，横向滚动时会离开视口。

透底问题与前台音乐库根因相同：`border-collapse: collapse` 会破坏 sticky z-index（已通过 separate 缓解）；行 hover / `is-active` 使用 `rgba` 半透明背景叠加在冻结列上时，下方滚动列文字仍可见。前台 `.studio-library-table` 已用「每个 td 施加实色背景 + 分层 z-index + 行态时 tr 背景透明」方案修复。

## Goals / Non-Goals

**Goals:**

- 横向滚动任意位置时，左侧勾选 + 歌曲、右侧操作三列冻结且不透底。
- 表头纵向 sticky（既有）与横向 sticky 列 z-index 协同，表头始终在冻结列最上层。
- hover / `is-active` / 勾选态下冻结列视觉与中间列一致。

**Non-Goals:**

- 不修改列集合、排序、分页或操作按钮行为。
- 不改动其它后台管理页表格（艺人、标签等）。
- 不改变 `/songs` API。

## Decisions

### 1. 为「歌曲」列引入 `col-title` 类

在 `admin.html` 表头 `<th>` 与 `admin.js` `renderSongs` 中歌曲 `<td>` 添加 `col-title`，与既有 `col-check`、`col-actions` 命名一致，便于 CSS 选择器维护。

**备选**：使用 `:nth-child(2)` —— 否决，DOM 变更时易失效，且与操作列 class 策略不一致。

### 2. CSS 变量定义冻结列宽度

在 `#admin-page-music .adm-songs-table` 上定义：

- `--adm-sticky-check-width`：勾选列宽度（约 44–48px，与现有 padding + checkbox 对齐）
- `--adm-sticky-title-width`：歌曲列宽度（约 180–200px，与前台 `--sk-lib-sticky-title-width` 对齐）

`col-check`：`left: 0`；`col-title`：`left: var(--adm-sticky-check-width)`；`col-actions`：`right: 0`（保持）。

歌曲列第二 sticky 列加 `box-shadow: 6px 0 14px -4px rgba(0,0,0,0.45)` 分隔滚动区，与前台一致。

### 3. z-index 分层（对齐前台已验证方案）

| 层级 | 选择器 | z-index |
|------|--------|---------|
| 中间滚动列 tbody td | `:not(.col-check):not(.col-title):not(.col-actions)` | 0 |
| 中间列表头 th | `:not(.col-check):not(.col-title):not(.col-actions)` | 1–3 |
| 冻结数据列 | col-check / col-title / col-actions tbody td | 11–13 |
| 纵向 sticky 表头（非冻结列） | thead th | 2（既有） |
| 冻结列表头 | col-check / col-title / col-actions thead th | 21–25 |

左侧表头 z-index 随列递增（check < title），右侧 actions 表头最高，避免 corner 叠盖错乱。

### 4. 实色背景与行态 td 规则

- 将 `--adm-sticky-bg-hover`、`--adm-sticky-bg-active` 改为**不透明** hex 色（参考前台 `#1c1a2e`、`rgba(108,71,255,0.22)` 的 active 可保留但需确保底层 td 有实色 `--adm-sticky-bg`）。
- 所有 tbody `td`（含中间列）设置 `background-color: var(--adm-sticky-bg)`，`position: relative; z-index: 0`。
- 行 hover / `is-active` 时：`tr { background: transparent }`，改为对每个 `td` 设置对应背景色，避免 tr 半透明叠加。

**备选**：伪元素 `::after` 遮罩 —— 仅在 separate + 实色背景仍不足时追加；优先 td 背景方案。

### 5. 歌曲列文本溢出

`col-title` 设置 `overflow: hidden; text-overflow: ellipsis; white-space: nowrap`（或 max-width 约束），避免长标题撑破冻结列宽。

### 6. 缓存版本

若 `admin.html` 引用 `admin-studio.css?v=`，递增版本号。

## Risks / Trade-offs

- **[Risk] 双列 sticky left 在 Safari 旧版偶发 1px 缝隙** → 使用 `background-clip: padding-box` 与 box-shadow 分隔线掩盖；与前台同源方案。
- **[Trade-off] 歌曲列固定宽度截断长标题** → 用户可通过横向滚动查看完整行其它字段；完整标题仍在编辑抽屉可见。
- **[Risk] 实色背景与主题变量不一致** → hover/active 色从 `--adm-bg` 派生不透明变体，保持暗色主题一致。

## Migration Plan

纯前端静态资源更新；部署后依赖 `?v=` bump。无数据迁移。回滚为三文件还原。

## Open Questions

（无）
