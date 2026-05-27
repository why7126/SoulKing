## 1. 后端：歌词文件名规范化

- [x] 1.1 在 `app/services.py` 新增 `derive_lyric_original_filename(db, song_id)`：复用 `choose_best_file` / `audio_song_files` 选取主音频 stem，回退 `lyrics.lrc`
- [x] 1.2 修改 `ingest_lyric_file()`：写入前调用推导函数设置 `original_filename`，再计算 object_key
- [x] 1.3 确认 `try_attach_sidecar_lrc` 与 `POST /songs/{id}/lyrics` 均经 `ingest_lyric_file`，无需额外传参
- [x] 1.4 手动或脚本验证：有 `MySong.flac` 时上传 `custom.lrc`，GET lyrics 返回 `filename: MySong.lrc`

## 2. 前端：歌词行显示切换

- [x] 2.1 `index.html`：为「词」按钮添加 `id="playerLyricsToggleBtn"`
- [x] 2.2 `studio.css`：新增 `.studio-player.is-lyrics-hidden` 隐藏歌词行；定义紧凑高度变量并联动主内容 `padding-bottom`
- [x] 2.3 `frontend.js`：实现 `togglePlayerLyricsVisible()`，更新 `aria-pressed`、`.is-active`、`title`
- [x] 2.4 `frontend.js`：页面初始化时从 `localStorage`（`sk.player.lyricsVisible`）恢复状态
- [x] 2.5 绑定 `#playerLyricsToggleBtn` 点击事件

## 3. 验收

- [x] 3.1 前台：点击「词」按钮隐藏/显示歌词行，列表末行不被遮挡，刷新后偏好保留
- [x] 3.2 后台：上传与侧车入库后 `#editLyricName` 与 API `filename` 与主音频 stem 一致
- [x] 3.3 隐藏歌词行时播放进度仍更新 `#playerLyricLine`（DOM 可隐藏），再次显示时文案正确
