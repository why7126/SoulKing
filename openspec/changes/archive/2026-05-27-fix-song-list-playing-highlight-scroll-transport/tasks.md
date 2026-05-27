## 1. 前台：滚动与跨页

- [x] 1.1 在 `app/static/frontend.js` 的 `scrollActiveSongItemIntoView`（或抽取的共用函数）中实现方案 A：读取 `wrap.querySelector("thead")` 的 `offsetHeight`，从计算得到的 `nextTop` 中减去该高度（可加 2–4px 常量间隙）；确认音乐库 `#songList` 与歌单详情 `playlistDetailSongList` 的 `closest(".song-table-wrap")` / `.pd-table-wrap` 均能解析到正确滚动容器。
- [x] 1.2 在 `playSong`（及必要时 `loadSongs` 完成后的回调链）中实现跨页：根据 `songListTotal`、`songPageSize`、目标曲在队列中的全局索引或 `song.id` 在服务端排序下的位置，设置 `state.songPage` 并 `await loadSongs({ resetPage: false })`，确保渲染后存在 `tr.is-active` 再滚动。
- [x] 1.3 手动验证：音乐库与歌单详情页分别上一首/下一首、长列表滚动，确认播放行不被表头遮挡且跨页后高亮正确。

## 2. 后台：双态高亮、滚动与跨页

- [x] 2.1 在 `app/static/admin.js` 中为播放行引入独立 class（如 `is-playing`），在 `renderSongs` 中根据 `state.currentPlayIndex` 与 `state.playQueue`/`state.songs` 关系标记行；保留 `is-active` 仅用于编辑选中（`activeSongId`）；同行仅保留播放态样式逻辑。
- [x] 2.2 在 `playSongInAdmin`、上一首/下一首、`ended` 处理中于播放索引变更后调用 `renderSongs()`（或轻量更新行 class 的 helper），并实现与前台同意图的 `scrollAdminPlayingRowIntoView`（容器 `.adm-table-scroll`，减 `thead` 高度）。
- [x] 2.3 实现后台跨页：切歌目标不在当前页时更新 `state.songPage` 并 `await loadSongs()`，再继续播放 UI 同步。
- [x] 2.4 手动验证：播放中打开另一曲编辑、冻结列横向滚动、跨页切歌。

## 3. 样式：后台播放态对齐前台

- [x] 2.5 在 `app/static/admin-studio.css`（必要时 `studio.css`）为 `tbody tr.is-playing td` 配置与前台 `.front-app .studio-library-table tbody tr.is-active td` 一致或同 token 的背景与层级；为 `is-active`（编辑）定义较弱对比；处理 hover 与双态优先级。

## 4. Transport 圆钮居中（回归）

- [x] 4.1 对照 `openspec/specs/web-static-client-shells/spec.md` 中「Studio 播放器 transport 圆钮图标居中」：检查 `studio.css` / `admin-studio.css` / `styles.css` 是否已覆盖圆钮 `padding` 与 `grid` 居中；若未满足则补齐选择器，使前后台 ⏮/▶/⏸/⏭ 几何居中。
- [x] 4.2 在前后台各切换播放/暂停一次，确认无偏移回归。

## 5. 收尾

- [x] 5.1 自查无控制台错误；必要时更新 `openspec/specs/web-static-client-shells/spec.md` 基线（仅当选择将增量需求上收主 spec 时，通常在 archive 阶段处理）。
