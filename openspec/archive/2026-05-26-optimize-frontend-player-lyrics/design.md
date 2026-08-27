## Context

- 前台播放器已采用紧凑两行布局（控制行 + 歌词行），CSS 通过 `--sk-player-total-h` 为主内容区预留底部空间。
- `#playerLyricLine` 与 LRC 同步逻辑已在 `frontend.js` / `lrc.js` 实现；控制行右侧「词」按钮（`.sk-pl-aux`）无 `id`、无事件绑定。
- 歌词入库走 `ingest_lyric_file()`：侧车扫描使用 `lrc_path.name`，后台上传使用 `file.filename` 作为 `original_filename`；对象键 stem 取自该字段。当上传名与音频 stem 不一致时，MinIO 路径与后台 `#editLyricName` 展示会偏离 `{audio_stem}.lrc` 约定。
- 试听择轨已有 `choose_best_file()`，可作为「主音频」命名参照的唯一来源。

## Goals / Non-Goals

**Goals:**

- 点击「词」按钮切换歌词行显示/隐藏，播放器高度与主内容 `padding-bottom` 联动。
- 歌词入库时 `original_filename` 统一为 `{主音频 stem}.lrc`，并触发 object_key 按现有规则重算。
- 切换状态在页面刷新后保持（`localStorage`）。

**Non-Goals:**

- 全屏歌词、后台播放器歌词切换、逐字卡拉 OK。
- 强制迁移历史已入库但文件名不一致的 LRC（除非用户触发「保存元数据/搬迁」类既有流程）。
- 修改歌词 API 响应结构。

## Decisions

### 1. 歌词行切换：CSS 类 + 高度变量

**选择**：在 `.studio-player` 上切换 `is-lyrics-hidden` 类；隐藏时 `.studio-player-row--lyrics { display: none }`，并定义 `--sk-player-total-h-compact`（不含歌词行高度）供 `.front-app` 主内容区使用。JS 在切换时给 `document.documentElement` 或 `.front-app` 设置 `data-lyrics-visible="false"` 以驱动 CSS 变量。

**理由**：与现有 `--sk-player-*` 体系一致，无需 JS 测量 DOM 高度。

**备选**：内联 `style.height` —— 难维护且与侧栏过渡不同步。

### 2. 按钮标识与可访问性

**选择**：为歌词按钮增加 `id="playerLyricsToggleBtn"`；切换时更新 `aria-pressed` 与 `title`（「隐藏歌词」/「显示歌词」）；激活态加 `.is-active`。

**理由**：便于测试与屏幕阅读器；与现有 ghost 按钮样式一致。

### 3. 状态持久化

**选择**：`localStorage` 键 `sk.player.lyricsVisible`，值 `"1"` / `"0"`；默认 `"1"`（显示，保持现行为）。

**理由**：轻量、无后端；符合播放器 UI 偏好场景。

### 4. 歌词文件名：服务层统一推导

**选择**：新增 `derive_lyric_original_filename(db, song_id) -> str`：

1. 查询歌曲下全部 `SongFile`，过滤 `format != lrc`。
2. 若存在音频，对 `choose_best_file(audio_files)` 的 `original_filename` 取 `Path.stem`，拼接 `.lrc`。
3. 若无音频，回退 `"lyrics.lrc"`（与 API 现有 fallback 一致）。

在 `ingest_lyric_file()` 内，忽略调用方传入的 `original_filename`（或仅作日志），一律使用推导结果写入 `SongFile.original_filename` 并计算 object_key。

侧车 `try_attach_sidecar_lrc` 与 `POST /songs/{id}/lyrics` 均走同一函数，行为一致。

**理由**：单点保证命名一致；object_key 与展示名对齐。

**备选**：仅在上传时重命名 —— 侧车与上传路径仍可能不一致。

### 5. 已有 LRC 记录的 object_key

**选择**：新入库/替换时按新 `original_filename` 计算 key；不单独写迁移脚本。若歌曲元数据保存已触发 `relocate_song_files_storage()`，LRC 会随 `original_filename` 一并搬迁。

**理由**：最小变更；历史不一致记录可在下次替换歌词或元数据搬迁时自然修正。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 隐藏歌词行后用户不知歌词仍在同步 | 按钮 `aria-pressed` 与激活样式；再次点击可恢复 |
| 多音频 stem 不同（罕见） | 以 `choose_best_file` 为准，与试听一致 |
| 推导 stem 含特殊字符 | 复用 `sanitize_path_segment` 于 object_key 路径；`original_filename` 保留原始 stem + `.lrc` |
| localStorage 不可用 | 捕获异常，回退会话内默认显示 |

## Migration Plan

1. 部署后端：新歌词入库立即使用规范文件名；不影响已有记录读取。
2. 部署前端静态资源：默认显示歌词行，老用户无感知。
3. 回滚：移除前端切换逻辑与 CSS 类；后端可保留推导逻辑（向前兼容）。

## Open Questions

- 全屏按钮（⛶）仍无功能 —— 本变更不处理。
- 是否在后台 `#editLyricName` 只读展示推导名 —— 建议随入库逻辑自动一致，无需额外 UI。
