## 1. 后端基础：歌词入库与解析

- [x] 1.1 在 `app/services.py` 新增 `LYRIC_EXTENSIONS`、`parse_lrc_content()`、`ingest_lyric_file()`、`get_song_lyric_file()`、`replace_song_lyrics()`（含删除同曲旧 LRC 及对象）
- [x] 1.2 确保 `choose_best_file`、`resolve_song_files_for_download`、`effective_is_playable_web` 等择轨/下载路径排除 `format=lrc`
- [x] 1.3 在 `app/schemas.py` 新增 `LyricLineOut`、`SongLyricsOut` 响应模型

## 2. 后端 API

- [x] 2.1 实现 `GET /songs/{song_id}/lyrics`（无歌词返回 404）
- [x] 2.2 实现 `POST /songs/{song_id}/lyrics`（multipart 单文件 `.lrc`，512KB 上限）
- [x] 2.3 实现 `DELETE /songs/{song_id}/lyrics`
- [x] 2.4 在 `SongDetailOut` / 列表响应中可选暴露 `has_lyrics` 或依赖 `files` 中 `format=lrc`（与现有 `admin.js` 检测一致）

## 3. 扫描侧车关联

- [x] 3.1 在 `scan_directory` / `ingest_file` 成功路径后查找同目录 `{stem}.lrc` 并调用 `ingest_lyric_file`
- [x] 3.2 侧车失败写入 `skipped_details`，不影响音频入库结果
- [x] 3.3 确认扫描前 `total_count` 枚举仍仅统计音频后缀

## 4. 共享前端工具

- [x] 4.1 新增 `app/static/lrc.js`：`findLyricLineAtTime(lines, timeMs)` 及可选客户端 `parseLrc` fallback
- [x] 4.2 在 `index.html`、`admin.html` 引入 `lrc.js`（在 `frontend.js` / `admin.js` 之前）

## 5. 前台播放器与检查器

- [x] 5.1 在 `frontend.js` 增加歌词状态（`lyricLines`、`lyricSongId`）与 `loadSongLyrics(songId)`
- [x] 5.2 在 `playSong` / `updatePlayerShell` 切歌时加载歌词；`timeupdate` 调用 `syncPlayerLyricLine`
- [x] 5.3 实现检查器「歌词」Tab 渲染（全文 / 无歌词提示）
- [x] 5.4 修复 Tab 切换：更新 `state.inspectorTab` 并切换面板内容

## 6. 后台编辑与播放器

- [x] 6.1 实现 `editLyricReplaceBtn`：文件选择 `.lrc` → `POST /songs/{id}/lyrics` → 更新 `#editLyricName`
- [x] 6.2 后台播放器 `#adminPlayerLyricLine` 复用歌词加载与同步逻辑（与前台一致）
- [x] 6.3 打开编辑抽屉时继续从 `detail.files` 显示 LRC 文件名

## 7. 样式与验收

- [x] 7.1 确认 `#playerLyricLine` 长歌词单行 ellipsis 仍符合 `studio.css` 两行布局
- [x] 7.2 手动验收：侧车扫描、后台上传、播放同步、切歌、无 LRC 占位、检查器 Tab
- [x] 7.3 手动验收：批量下载 ZIP 不含 `.lrc`；试听择轨不受 LRC 影响
