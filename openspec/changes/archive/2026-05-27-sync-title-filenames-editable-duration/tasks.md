## 1. 服务端：标题变更联动文件名

- [x] 1.1 在 `app/services.py` 新增 `sync_song_file_names_to_title(db, song)`：遍历该曲全部 `SongFile`，音频设为 `{sanitize_path_segment(title)}.{fmt}`，歌词（`format==lrc`）设为 `{stem}.lrc`；扩展名与 `patch_song_file` 校验规则一致
- [x] 1.2 在 `app/main.py` 的 `update_song` 中：当 `payload.title` 去空白后与旧 `song.title` 不同时，在写入新 title 后、`db.flush()` 前调用 `sync_song_file_names_to_title`；保持其后 `relocate_song_files_storage` 调用顺序不变
- [x] 1.3 手动或脚本验证：改 title 保存后 `original_filename` 与 S3 `object_key` 路径段一致；未改 title 时文件名不变

## 2. 管理端：可编辑时长（mm:ss）

- [x] 2.1 修改 `app/static/admin.html`：移除 `#durationDisplay` 的 `readonly`，设置 `placeholder="00:00"`；移除或停止依赖 hidden `#durationInput`
- [x] 2.2 在 `app/static/admin.js` 新增 `parseDurationMmSs` / `formatDuration` 配套校验；`openEditModal` 继续用 `formatDuration` 填充展示字段
- [x] 2.3 更新 `saveSingleMetadata`：从 `#durationDisplay` 解析 `duration_ms`（空→null，`00:00`→0）；非法格式 toast 并 return
- [x] 2.4 可选：在时长字段 `blur` 时将输入规范为两位分钟与两位秒（如 `3:5` → `03:05`）

## 3. 验收

- [x] 3.1 编辑歌曲：仅改 title 保存 → 音频列表与歌词展示名均为新标题 stem + 对应扩展名
- [x] 3.2 编辑歌曲：修改时长为 `04:30` 保存 → 列表时长列与再次打开抽屉一致
- [x] 3.3 编辑歌曲：清空时长保存 → 列表显示为未知或 `—`（与现有无时长展示一致）
