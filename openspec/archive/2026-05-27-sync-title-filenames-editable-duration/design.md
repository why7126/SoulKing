## Context

后台歌曲编辑通过 `PUT /songs/{id}` 更新元数据。保存末尾已调用 `relocate_song_files_storage`，按 `music/{原唱}/{歌名}/{stem}.{格式}` 重算 `object_key`，其中 `stem` 取自各 `SongFile.original_filename`，**不会**因 title 变更而自动更新。管理端 `#durationDisplay` 为只读，`#durationInput` 隐藏存毫秒，用户无法在 UI 修正时长。

## Goals / Non-Goals

**Goals:**

- 标题变更时，在同一 PUT 事务内将所有关联音频与歌词的 `original_filename` 统一为 `{sanitize(新标题)}.{扩展名}`，再执行存储搬迁。
- 管理端编辑抽屉允许以 `mm:ss` 编辑时长，校验通过后转换为 `duration_ms` 提交。

**Non-Goals:**

- 不实现「仅当 stem 等于旧标题时才重命名」的保守规则（已选定规则 1：全部统一）。
- 不改动批量更新 API 的 title 联动（本变更仅覆盖单曲 `PUT`；批量若未传 title 则不受影响）。
- 不新增 `H:MM:SS` 或小时级输入；与列表展示一致，采用 `mm:ss`（分钟至少两位、秒两位）。
- 不自动从音频文件重新探测时长覆盖用户手填值。

## Decisions

### 1. 服务端在 `update_song` 内联动重命名（方案 A）

**选择**：在 `app/main.py` 的 `update_song` 中，检测到 `payload.title` 非空且 strip 后与 `song.title` 不同后，调用 `services.sync_song_file_names_to_title(db, song)`，再 `db.flush()` 与 `relocate_song_files_storage`。

**理由**：与现有 PATCH 单文件重命名 + relocate 模式一致，一次保存原子完成，避免前端多次 PATCH 半失败。

**备选**：前端保存后对每个 file PATCH —— 已否决（非原子、复杂）。

### 2. 命名规则：全部文件 stem = sanitize(新标题)

**选择**：

- 音频：`original_filename = f"{stem}.{fmt}"`，其中 `stem = sanitize_path_segment(song.title, "untitled", 180)`，`fmt` 为既有 `song_file.format`（小写、无点前缀）。
- 歌词（`format == lrc`）：`original_filename = f"{stem}.lrc"`，与音频 stem 一致（不再单独走 `derive_lyric_original_filename` 读旧音频 stem）。

**理由**：满足规则 1；多格式并存时均为「新歌名.mp3」「新歌名.flac」；LRC 与主音频展示名对齐。

**备选**：保守匹配旧 title —— 用户已选规则 1。

### 3. 仅在 title 实际变更时触发

**选择**：比较 strip 后的旧 `song.title` 与新值；相同则跳过 `sync_song_file_names_to_title`（仍可按其它元数据变更执行 relocate）。

**理由**：避免无意义写入与 S3 copy。

### 4. 时长 UI：`durationDisplay` 可编辑 + 解析函数

**选择**：

- 移除 `#durationDisplay` 的 `readonly`；移除或弃用 hidden `#durationInput`，保存时从 display 解析。
- 新增 `parseDurationMmSs(text)`：匹配 `^(\d{1,3}):([0-5]\d)$`（分钟 1–3 位、秒 00–59）；返回 `minutes * 60000 + seconds * 1000`。
- 新增 `normalizeDurationMmSs(text)`：blur 或保存前将 `3:5` 规范为 `03:05`（可选，保存前至少校验）。
- 空字符串 → 提交 `duration_ms: null`；`00:00` → `0`。
- 非法格式：阻止 submit，`showToast` 提示「时长格式应为 mm:ss，例如 03:45」。

**理由**：与现有 `formatDuration` 输出一致；后端已支持 `duration_ms`，无需 API 变更。

**备选**：保留 hidden input 由 display 同步 —— 可简化 save 逻辑，但单字段更易维护。

### 5. 校验与 PATCH 重命名规则对齐

**选择**：新 stem 非空；不含 `/`、`\`；扩展名与 `format` 一致（与 `patch_song_file` 相同约束）。复用 `sanitize_path_segment` 处理非法路径字符。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 用户曾手动重命名的变体 stem 被覆盖 | 已在 proposal 明确为规则 1；产品接受 |
| title 含特殊字符导致 stem 被 sanitize 后与显示 title 不完全一致 | 与现有 object_key / 下载命名行为一致 |
| 多文件同 format 罕见冲突 | `compute_music_object_key` 已有 sha 后缀消歧 |
| S3 copy 失败时 silent continue（既有行为） | 不扩大 scope；文件名 DB 仍更新 |
| 超长歌曲 >999 分钟 | 正则允许 3 位分钟；与 `formatDuration` 对长时长展示兼容 |

## Migration Plan

- 纯行为增强，无数据库 schema 变更。
- 部署后：用户改 title 并保存即触发联动；历史数据不批量迁移。
- 回滚：还原 `update_song` 与 admin 前端即可；已改名的文件不会自动回滚。

## Open Questions

（无 —— 时长空值与 `00:00` 语义、规则 1、方案 A 已在 explore 阶段确认。）
