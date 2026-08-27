## Context

- 歌词 UI 壳层已存在：`#playerLyricLine`、`#adminPlayerLyricLine`、检查器「歌词」Tab、后台 `editLyricName`；`admin.js` 仅在编辑抽屉中按 `detail.files` 匹配 `.lrc` 文件名，上传按钮为 Toast 占位。
- 音频入库走 `SUPPORTED_EXTENSIONS`，`SongFile` + MinIO `music-files`；`is_playable_web` 控制试听择轨。
- 探索结论：无 `.lrc` 入库路径、无歌词 API、前台 `updatePlayerShell` 不更新歌词行。

## Goals / Non-Goals

**Goals:**

- 支持 `.lrc` 作为歌曲附属文件入库（扫描侧车、后台上传/替换）。
- 每首歌曲至多一条「当前有效」LRC（新上传或扫描关联时替换旧记录及对象）。
- 提供 `GET` 歌词文本接口供前台/后台读取（UTF-8，兼容常见 LRC 时间标签）。
- 前台播放时按 `currentTime` 在 `#playerLyricLine` 显示当前行；检查器「歌词」Tab 展示全文。
- 歌词文件 `format=lrc`、`is_playable_web=false`，不参与试听/批量音频下载。

**Non-Goals:**

- 卡拉 OK 逐字、翻译轨、`.txt` 纯文本歌词、在线歌词搜索、歌词编辑/时间轴编辑器、全屏歌词页、播放器「词」按钮弹层（可保留无操作或滚动到歌词行）。

## Decisions

### 1. 复用 `SongFile` 而非新表

**选择**：`.lrc` 存为 `song_files` 一行，`format=lrc`，`is_playable_web=false`，`is_lossless=false`；对象键仍走 `compute_music_object_key`（扩展名 `.lrc`）。

**理由**：与现有存储、删除、搬迁逻辑一致；`detail.files` / `file_variants` 已暴露给前端。

**备选**：独立 `song_lyrics` 表 —— 增加迁移与 API 面，收益有限。

### 2. 格式白名单拆分

**选择**：新增 `LYRIC_EXTENSIONS = {".lrc"}`；`ingest_lyric_file()` 独立函数；扫描在音频 `ingest_file` 成功后尝试侧车关联。

**理由**：避免 LRC 进入 `extract_metadata` / 试听优先级；目录扫描仍只把音频计入 `scanned_count`，LRC 关联记入跳过明细或子统计（实现可选「关联成功」不计入 skipped）。

**侧车匹配规则**：同目录下 `{audio_stem}.lrc`（大小写不敏感）对应刚入库或匹配到的 `song_id`；若该曲已有 LRC，则删除旧对象与记录后写入新文件（与上传替换一致）。

### 3. 每曲一条有效 LRC

**选择**：`get_song_lyric_file(db, song_id)` 取 `format=lrc` 的最新一条（`id` 最大）；上传/扫描替换时删除同曲其它 `format=lrc` 行及对象。

**理由**：简化播放器与 API；多版本 LRC 非 MVP 需求。

### 4. 歌词 API

**选择**：

- `GET /songs/{song_id}/lyrics` → `{ "filename": "...", "content": "...", "lines": [{ "time_ms": 12340, "text": "..." }] }`（`lines` 为服务端解析结果，便于前端；解析失败时仍返回 `content` 与空 `lines`）。
- `POST /songs/{song_id}/lyrics`（multipart 单文件 `.lrc`）→ 替换并返回与 GET 相同结构。
- `DELETE /songs/{song_id}/lyrics` → 删除当前 LRC。

鉴权与现有管理/前台 API 一致（单租户，无额外登录）。

**备选**：仅返回原始文本、前端解析 —— 减少重复解析逻辑，但后台与前台需各实现一份；**采用服务端解析 + 共享静态 `parseLrc()` 作为 fallback**（网络失败时不可用，正常走 API）。

### 5. 前端同步

**选择**：`frontend.js` 在 `playSong` / `timeupdate` 中维护 `state.lyricLines` 与 `state.lyricSongId`；切换歌曲时 `fetch` 歌词 API；`syncPlayerLyricLine(currentTimeMs)` 二分/线性查找当前行。

**占位**：无歌词时 `#playerLyricLine` 为「当前暂无歌词同步显示」；有歌词无匹配行时显示「···」或空行。

**检查器**：Tab `data-tab=lyrics` 切换时渲染 `<pre>` 或分行列表；未选曲或未加载时提示。

**共享**：`app/static/lrc.js` 导出 `parseLrc(text)`，供前端可选本地校验；主路径用 API `lines`。

### 6. 批量下载与择轨隔离

**选择**：`choose_best_file`、`resolve_song_files_for_download`、`effective_is_playable_web` 逻辑不变；显式过滤 `format != lrc`。

**理由**：避免 ZIP 混入歌词除非未来单独选项（本变更不做）。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| LRC 编码非 UTF-8（GBK） | 上传/读取时尝试 UTF-8，失败则 `chardet` 或回退 Latin-1 并记录；文档说明推荐 UTF-8 |
| 扫描时音频与 LRC 不同步入库顺序 | 仅在音频成功入库后同轮查找侧车；音频跳过则不关联 |
| 大 LRC 文件拖慢 GET | 限制单文件大小（如 512KB）；超限拒绝上传 |
| `timeupdate` 频繁更新 DOM | 仅当行文本变化时更新 `textContent` |
| 合并歌曲后多 LRC 行 | 合并逻辑沿用 `SongFile` 改挂；合并后按 song_id 去重保留最新 |

## Migration Plan

1. 部署后端（新端点 + 扫描侧车 + `ingest_lyric_file`）。
2. 部署前端静态资源（`lrc.js`、`frontend.js`、`admin.js`）。
3. 无需 DB 迁移；已有库无 LRC 时行为与现在占位一致。
4. **可选回填**：用户对含侧车 LRC 的目录重新扫描不会重复音频（去重跳过），需单独「关联歌词」工具 —— **本变更不做**，仅新入库音频触发侧车。

**回滚**：移除端点与前端调用；已入库 LRC 行可保留，不影响播放。

## Open Questions

- 是否在扫描进度 UI 中单独展示「已关联歌词 N 条」？（建议 tasks 中作为可选增强）
- 后台播放器是否同步 LRC 行？（建议与前台一致，实现成本低）
