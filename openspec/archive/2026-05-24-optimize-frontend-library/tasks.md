## 1. 顶栏与布局

- [x] 1.1 在 `studio.css` 中为 `.studio-root.is-library-view .studio-top-header` 添加隐藏样式（`display: none` 或等效零高度），确保不占用垂直空间
- [x] 1.2 验证歌单/其它非音乐库视图顶栏仍正常显示；⌘K 快捷键仍聚焦 `#libraryKeywordInput`

## 2. 服务端分页

- [x] 2.1 在 `frontend.js` 新增 `buildFrontSongListQueryParams()`，对齐 admin：含筛选参数、`offset`、`limit=state.songPageSize`
- [x] 2.2 修改 `loadSongs()`：音乐库路径使用上述 params 请求 `/songs`；保留 `state.songListTotal = page.total`；筛选变更时 `songPage = 1`，翻页时不强制重置为 1
- [x] 2.3 修改 `renderSongList()`：移除对 `state.songListTotal = state.songs.length` 的覆盖；序号仍用 `(songPage-1)*pageSize + index`
- [x] 2.4 修改 `updateFrontPaginationUi()`：翻页按钮、页码按钮点击时调用 `loadSongs()` 而非仅 `renderSongList()`
- [x] 2.5 修改 `frontPageSizeSelect` 变更处理：重置页码并 `loadSongs()`
- [x] 2.6 在 `index.html` 页脚增加 `#frontPageInfoLabel`（或扩展 `#frontSongListTotalLabel`），展示「显示 A–B，共 N 首」与「第 X / Y 页」

## 3. 操作列与收藏移除

- [x] 3.1 在 `studio.css` 为 `.sk-row-actions button` 添加 `display: grid; place-items: center`
- [x] 3.2 从 `songRowInnerHtml()` 移除 `data-role="fav"` 按钮及对应 click handler
- [x] 3.3 从 `index.html` 移除或 `hidden` 播放器 `.sk-player-heart`、`#inspectorFavoriteBtn`、音质「调」按钮
- [x] 3.4 确认歌单详情行模板 `songRowPlaylistDetailInnerHtml` 中收藏按钮一并移除（若存在）

## 4. 播放模式下拉

- [x] 4.1 在 `index.html` transport 区：移除 `#repeatModeBtn` 与 `#shuffleToggleBtn`；将 `#playModeSelect` 改为可见并补充中文 option 文案
- [x] 4.2 在 `studio.css` 为可见播放模式下拉添加 Studio 风格样式
- [x] 4.3 在 `frontend.js`：`playModeSelect` change 事件更新 `state.playMode`；简化或移除 `repeatModeBtn`/`shuffleToggleBtn` 相关 listener；更新 `syncTransportDecorations()`

## 5. 表格冻结列

- [x] 5.1 在 `studio.css` 为 `.studio-library-table` 的 `.sk-col-idx`、`.sk-col-title`（th/td）实现 sticky（left 偏移、背景色、z-index）
- [x] 5.2 处理 hover 行背景与 thead 层级；必要时设置 `border-collapse: separate` 以确保 sticky 生效
- [x] 5.3 手动验证横向滚动时 # 与歌曲列固定、后续列正常滚动

## 6. 验收

- [x] 6.1 曲库 >20 首时验证翻页、改每页条数、页脚文案正确
- [x] 6.2 验证筛选后 total 与页码重置行为
- [x] 6.3 验证无顶栏空白、无收藏/调占位、播放模式下拉四项可用
- [x] 6.4 更新 `index.html` / `frontend.js` / `studio.css` 缓存版本 query（`?v=`）若项目惯例需要
