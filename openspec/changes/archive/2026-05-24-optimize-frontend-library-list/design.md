## Context

前台音乐库表格同时带有 `.song-table` 与 `.studio-library-table` 类名。`.song-table` 全局使用 `border-collapse: collapse`，而后台歌曲管理页注释已说明 collapse 会导致同行单元格 z-index 失效，横向滚动时滚动列会盖住 sticky 列。`.studio-library-table` 虽单独设置了 `border-collapse: separate`，但可能被 `.song-table` 规则覆盖或 z-index 层级不足，导致冻结列下方滚动列文字透出。

操作列当前在 `songRowInnerHtml` 中渲染四个并排图标按钮（▶、＋、↓、⋯），「更多」点击仅 toast 占位。后台 `admin.js` 已有 `table-more` / `table-more-menu-fixed` 模式，可将菜单挂到 `document.body` 避免 overflow 裁剪。

## Goals / Non-Goals

**Goals:**

- 横向滚动任意位置时，左/右冻结列完全遮挡下方中间列，无文字或控件重叠。
- 音乐库操作列默认只显示「更多」按钮；试听、加入歌单、下载在下拉菜单中可用且行为与现有一致。
- 操作列宽度收窄，sticky 右缘布局稳定。

**Non-Goals:**

- 不修改歌单详情页（`songRowPlaylistDetailInnerHtml`）操作布局。
- 不在「更多」菜单中新增尚未实现的操作（除将既有三个入口移入外）。
- 不改变 `/songs` API 或列集合定义。

## Decisions

### 1. 强制音乐库表格使用 `border-collapse: separate`

为 `.front-app .song-table.studio-library-table` 显式设置 `border-collapse: separate; border-spacing: 0`，优先级高于通用 `.song-table` 的 collapse，与后台 `#admin-page-music .admin-table` 方案一致。

**备选**：仅提高 z-index —— 否决，collapse 下 sticky z-index 行为不可靠。

### 2. 分层 z-index 与实色背景

- 中间滚动列（`tbody td.sk-col-meta` 等）：不设 sticky，`z-index: auto`。
- 冻结数据列（`sk-col-idx` / `sk-col-title` / `sk-col-actions`）：`z-index: 3`，实色 `background-color` + `background-clip: padding-box`。
- 冻结表头：在数据列基础上 `z-index: 5`，背景 `--sk-panel-2`。
- 左侧 `#` 列 z-index 略低于 `歌曲` 列（或递增），避免多列 sticky left 叠盖异常；右侧操作列与表头同级。

补充 hover / `.is-active` / `.is-selected` 背景规则，确保各态下不透明。

**备选**：伪元素遮罩层 —— 仅在 separate + 背景仍不足时追加，优先 CSS 变量背景方案。

### 3. 操作列 DOM 改为 `sk-row-more` 下拉

`songRowInnerHtml` 操作列结构：

```html
<td class="sk-col-actions" data-stop-row="1">
  <div class="sk-row-more">
    <button data-role="more" aria-label="更多">⋯</button>
    <div class="sk-row-more-menu hidden" data-role="menu">
      <button data-role="play">▶ 试听</button>
      <button data-role="add">＋ 加入歌单</button>
      <button data-role="download">↓ 下载</button>
    </div>
  </div>
</td>
```

（示意结构，实际类名遵循 `sk-` 前缀。）

菜单展开逻辑参考后台：toggle `hidden`；展开时将 menu 移至 `document.body` 并加 `sk-row-more-menu-fixed`，用 `getBoundingClientRect()` 定位；关闭时归还 DOM 并清 inline style。全局 click 关闭其它行已开菜单。

行点击播放/选中等行为在 `data-stop-row` 上 stop，避免误触。

**备选**：CSS `position: absolute` 不 portal —— 否决，`.song-table-wrap` 的 `overflow: auto` 会裁剪菜单。

### 4. 操作列常显 vs hover 显隐

当前 `.sk-row-actions` 默认 `opacity: 0`，hover 行才显示。收拢为单「更多」按钮后，改为操作列按钮**始终可见**（`opacity: 1`），避免用户找不到入口。

**备选\`--sk-lib-sticky-actions-width\`**：由 148px 降至约 52–64px（单 30px 按钮 + padding）。

### 5. 缓存版本

递增 `index.html` 内 `studio.css`、`frontend.js` 的 `?v=`。

## Risks / Trade-offs

- **[Risk] fixed 菜单定位在窗口 resize/scroll 时偏移** → 滚动表格或 resize 时关闭菜单；与后台一致。
- **[Risk] 操作多一步点击** → 换取更窄操作列与更整洁列表；常用试听仍可通过双击行/播放器队列触发（既有行为不变）。
- **[Trade-off] 歌单详情仍为多按钮** → scope 限定音乐库表，后续可单独统一。

## Migration Plan

纯前端静态资源更新；部署后依赖 `?v=` bump。无数据迁移。回滚为三文件还原。

## Open Questions

（无）
