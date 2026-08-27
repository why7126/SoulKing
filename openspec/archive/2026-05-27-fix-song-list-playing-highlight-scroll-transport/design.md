## Context

前台 `renderSongList` 在播放索引变化后为匹配行加 `is-active`，并在末尾调用 `scrollActiveSongItemIntoView()`；滚动容器为 `tbody` 祖先 `.song-table-wrap`，表头为 `position: sticky; top: 0`。后台 `renderSongs` 仅根据 `activeSongId`（点击行打开编辑）加 `is-active`；`playSongInAdmin` 更新 `currentPlayIndex` 但不驱动表格重绘或滚动。前后台列表均为服务端分页，队列默认来自当前页 `songs` 切片。

## Goals / Non-Goals

**Goals:**

- 播放行在滚动容器内完整可见，且不被 sticky 表头遮挡（方案 A：`nextTop = ... - thead.offsetHeight`，必要时加 2–4px 间隙）。
- 后台同时展示「正在播放」与「当前为编辑打开的歌曲」两种行态时，播放态更强且与前台播放行视觉一致（同一套紫色系背景策略：冻结列各 `td` 实色背景，避免透底）。
- 上一首/下一首/自动下一曲若目标曲不在当前页，自动切换页码并 `loadSongs`（或等价）后再高亮与滚动。
- 歌单详情内嵌表格路径与曲库一致，共用滚动修正逻辑。
- Transport 圆钮：与基线 spec 一致，覆盖 `styles.css` 默认 `button` padding，使用 `display: grid; place-items: center` 或等价。

**Non-Goals:**

- 不改变播放队列语义（仍可为当前页切片）；不引入全量曲库客户端队列。
- 不重做播放器布局或歌词面板行为。

## Decisions

1. **滚动算法（方案 A）**  
   在现有「将活动行顶边对齐容器内容顶」的基础上，减去 `wrap.querySelector('thead')?.offsetHeight ?? 0`（可加常量 `gap`）。若行底仍超出容器底，再补充一次判断：仅当行不在 `[theadH, clientHeight]` 可见带内时才滚动，避免无意义抖动（可选优化，任务中实现一项即可）。

2. **后台双态 class**  
   采用 `is-playing`（或项目内已有约定名）表示当前 `currentPlayIndex` 对应行；保留 `is-active` 表示「编辑选中 / 打开抽屉对应行」。CSS：`is-playing` 复用前台 `tbody tr.is-active td` 同级别变量（建议在 `admin-studio.css` 引用与 `studio.css` 相同的自定义属性或复制 `--sk-lib-sticky-bg-active` 数值），`is-active` 使用较弱背景与左侧条（与现有一致或略弱化）。**二者同时命中一行时**，播放态优先（或合并为播放态），避免双重边框冲突。

3. **跨页**  
   在 `playSong` / `playSongInAdmin`（及 prev/next/ended 调用链）中，根据目标 `songId` 与 `songListTotal`、`songPageSize` 计算 `requiredPage = floor(globalIndex / pageSize) + 1`；若 `globalIndex` 仅相对当前页可用（队列索引），则用 `offset + queueIndex` 与服务器 `total` 比较：若列表 API 支持按 id 定位则更佳，否则以「当前队列来自整库连续 offset」为前提计算页码——与现有 `syncQueue` / `playQueue` 实现一致：队列即当前页数组时，`globalIndex = (songPage-1)*pageSize + queueIndex`。切歌目标若不在本页，设置 `state.songPage = requiredPage` 并 `await loadSongs({ resetPage: false })` 后继续播放与高亮（注意避免递归重入）。

4. **Transport**  
   在 `.studio-transport .studio-transport-btn`（或实际选择器）上 `padding: 0`、`box-sizing: border-box`、`display: grid`、`place-items: center`，并检查 `line-height`/`font-size` 不撑破圆。前后台共用类名则一处修复两处受益。

## Risks / Trade-offs

- **[Risk] 跨页时 filter 变化导致目标 id 不在新页** → 若请求后列表中找不到该 id，Toast 提示并回退播放索引或保持播放器状态不刷列表。
- **[Risk] 双 class 与旧 E2E/截图测试** → 文档化 class 契约；编辑打开时仍应能看出播放行（若不同曲）。
- **[Risk] `offsetHeight` 在字体加载前后变化** → 可在 `requestAnimationFrame` 后二次 `scrollTo` 微调（可选）。

## Migration Plan

纯静态部署；无数据迁移。回滚为还原 JS/CSS。

## Open Questions

（无；产品选择已由变更请求确定：播放/编辑分行样式、跨页自动翻页、歌单详情一并验证。）
