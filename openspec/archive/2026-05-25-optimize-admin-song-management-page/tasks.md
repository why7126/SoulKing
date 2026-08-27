## 1. 操作列收敛为「更多」下拉

- [x] 1.1 在 `admin.js` 的 `renderSongs` 中移除 `edit-quick`、`play-quick`、`download-quick` 三个行内按钮 DOM
- [x] 1.2 扩展 `.table-more-menu`：按序添加「编辑」「播放/试听」「下载」菜单项，保留「删除」；不可播时播放项 disabled 并带 title
- [x] 1.3 将原快捷按钮事件处理器迁移至对应菜单项（编辑打开抽屉、播放调用 `playSongInAdmin`、下载调用 `startDownloadFlow`）
- [x] 1.4 调整 `admin-studio.css` 操作列宽度（`.col-actions` / `.adm-actions-inner`），确保仅 ⋮ 按钮时列宽合理

## 2. 编辑抽屉：影视剧与发行日期

- [x] 2.1 在 `admin.html` 将 `#filmTvInput` 移出 `adm-hidden-filters`，放入主表单可见栅格（如与发行日期/语言相邻）
- [x] 2.2 将 `#releaseDateInput` 改为 `type="date"`，更新 placeholder/label 文案为「发行日期」
- [x] 2.3 更新 `syncReleaseDateField` / `releaseDateFromForm`：读写 `YYYY-MM-DD`；对无法解析的历史值清空 date input
- [x] 2.4 确认 `openEditModal` 保存草稿/提交时 `film_tv` 与 `release_date` 仍正确提交；AI 建议应用路径同步日期规范

## 3. Studio 风格后台播放器

- [x] 3.1 在 `admin.html` 用 `.studio-player` 结构替换 `footer.admin-player-compact`（参考 `index.html`）；audio 保留 `#adminAudioPlayer` 且移除 `controls`
- [x] 3.2 引入/复用 `studio.css` 中播放器样式至 admin（`admin-studio.css` 扩展或 link `studio.css`），含侧栏收起 `left` 同步
- [x] 3.3 在 `admin.js` 新增播放器 UI 绑定：play/pause 图标、`timeupdate` 更新进度条与时间、进度条 click seek、音量、`ended` 切歌
- [x] 3.4 更新 `playSongInAdmin`（及文件预览播放路径）以刷新 `#adminPlayerBarTitle`、艺人/格式展示与 transport 状态
- [x] 3.5 为歌曲管理主内容区设置与播放器高度一致的 `padding-bottom`，避免列表末行被遮挡

## 4. 验证

- [x] 4.1 手动验证：操作列仅 ⋮，菜单内编辑/播放/下载/删除均可用；不可播曲目播放项 disabled
- [x] 4.2 手动验证：编辑抽屉可见影视剧、日期选择器选择与保存回显
- [x] 4.3 手动验证：底部播放器播放/暂停/切歌/进度/音量/播放模式与列表播放一致
