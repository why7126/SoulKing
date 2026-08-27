## Why

前台播放器与后台编辑抽屉已预留歌词 UI（`#playerLyricLine`、检查器「歌词」Tab、`.lrc` 文件名展示），但系统仅入库音频格式，无法导入、存储或按播放进度展示 LRC 歌词。用户本地常将 `.lrc` 与音频并排存放，期望像流媒体一样在试听时看到同步歌词；补齐该能力可提升播放体验并完成元数据治理闭环。

## What Changes

- 将 `.lrc` 纳入歌曲附属文件模型：作为 `SongFile` 记录写入对象存储（`is_playable_web=false`），与歌曲一对多关联，不参与试听择轨与下载 ZIP 的音频变体逻辑。
- **目录扫描**：与音频同目录、同主文件名的 `.lrc` 在音频入库成功后自动关联到同一首 `Song`（若音频新建或匹配到已有歌曲）。
- **后台**：实现编辑抽屉「替换歌词」上传；列表/详情可识别已关联 `.lrc`。
- **API**：提供按歌曲读取歌词文本（及可选元数据）的接口；不通过音频流接口返回歌词。
- **前台播放**：解析 LRC，在 `#playerLyricLine` 按 `audio.currentTime` 显示当前行；无歌词时保留占位文案。
- **检查器**：「歌词」Tab 展示全文（可滚动）；无歌词时说明如何关联。
- **范围外（本变更）**：逐字卡拉 OK、翻译轨、非 LRC 格式（如 `.txt` 纯文本）、歌词编辑器、全屏歌词面板。

## Capabilities

### New Capabilities

- `song-lyrics`：歌词文件的入库规则、存储形态、读取 API、与歌曲的关联及「每曲至多一条有效 LRC」的约定。

### Modified Capabilities

- `music-ingestion`：目录扫描时识别并关联同目录同名 `.lrc` 侧车文件。
- `song-files-and-storage-lifecycle`：向已有歌曲上传/替换 `.lrc`；删除歌词文件时的对象与记录清理。
- `web-static-client-shells`：前台播放器歌词行同步、检查器歌词 Tab；后台播放器歌词行可选展示文件名或当前行。

## Impact

- **后端**：`app/services.py`（扩展格式白名单或独立歌词入库路径）、`app/main.py`（歌词 GET/上传端点）、`ingest_file` / `scan_directory` 侧车逻辑。
- **存储**：MinIO `music-files` 桶内新增 `.lrc` 对象键（与现有 `compute_music_object_key` 体系一致或子路径 `lyrics/`）。
- **前端**：`frontend.js`、`admin.js`、`index.html`、`admin.html`；共享 LRC 解析工具（可放在静态 JS 模块或内联函数）。
- **数据**：`song_files` 表无 schema 迁移；依赖 `format=lrc` 与 `is_playable_web=false` 区分。
- **规范**：不影响 `audio-playback-and-download` 择轨语义；批量下载默认仍仅打包音频。
