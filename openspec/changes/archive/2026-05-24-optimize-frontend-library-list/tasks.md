## 1. 修复冻结列叠层透底

- [x] 1.1 在 `studio.css` 为 `.front-app .song-table.studio-library-table` 显式设置 `border-collapse: separate; border-spacing: 0`，覆盖通用 `.song-table` 的 collapse
- [x] 1.2 校准冻结列 z-index 分层（表头 > 数据冻结列 > 中间滚动列），确保 `#`/`歌曲`/`操作` 列实色背景在各态下不透明
- [x] 1.3 手动验证：横向滚动时中间列文字不透过左/右冻结列显示

## 2. 操作列「更多」下拉菜单

- [x] 2.1 在 `frontend.js` 的 `songRowInnerHtml` 将操作列改为单「更多」按钮 + 隐藏菜单（试听、加入歌单、下载）
- [x] 2.2 实现菜单展开/关闭逻辑（参考后台 `table-more-menu-fixed`：portal 到 `document.body`、定位、全局关闭）
- [x] 2.3 将菜单项 `play` / `add` / `download` 事件绑定到既有 `playSong`、`addSongToPlaylist`、`startSongDownloadFlow`，保留 disabled 与 title 提示
- [x] 2.4 为 `data-stop-row` 阻止行级点击冒泡，避免误触

## 3. 样式与列宽

- [x] 3.1 在 `studio.css` 新增 `sk-row-more` / `sk-row-more-menu` 样式（对齐前台 studio 视觉）
- [x] 3.2 操作列「更多」按钮改为常显（非 hover 才 opacity:1），并减小 `--sk-lib-sticky-actions-width`
- [x] 3.3 确保下拉菜单 z-index 高于表格 sticky 层，不被裁剪

## 4. 收尾

- [x] 4.1 递增 `index.html` 中 `studio.css`、`frontend.js` 的 `?v=` 缓存版本
- [x] 4.2 手动验证：操作列仅显示「更多」；菜单三项行为正确；横向滚动无叠字；歌单详情列表无回归
