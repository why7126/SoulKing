## 1. 样式修正

- [x] 1.1 在 `app/static/admin-studio.css` 中从 `#admin-page-music .adm-songs-table tbody tr.is-active td` 移除 `box-shadow: inset 3px 0 0`；保留 `--adm-sticky-bg-selected` 背景。
- [x] 1.2 删除或弱化 `.admin-app .adm-songs-table tbody tr.is-active:not(.is-playing)` 上与 `#admin-page-music` 重复的 `rgba` 背景及 `tr` 级 `box-shadow`，避免编辑行双重高亮。
- [x] 1.3（可选）若需保留「正在编辑」指示：仅为 `tr.is-active:not(.is-playing) td.col-check` 添加单条 `inset 3px 0 0 var(--adm-accent)`，其它 `td` 不得有 inset 竖条。

## 2. 验收

- [x] 2.1 打开编辑抽屉：编辑行弱于播放行，中间列无紫色竖条；播放 A、编辑 B 时两行可区分。
- [x] 2.2 横向滚动冻结列：编辑行在勾选/歌曲列区域至多一条左侧线（若启用 1.3），操作列无竖条。

## 3. 收尾

- [x] 3.1 确认 `is-playing` 样式未回归；无控制台/CSS 语法错误。
