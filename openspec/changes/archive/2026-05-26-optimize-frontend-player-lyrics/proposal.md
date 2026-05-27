## Why

前台底部播放器已具备歌词同步展示（`#playerLyricLine`）与「词」按钮，但歌词行始终占用第二行高度，且按钮未绑定任何交互；在曲库浏览场景下用户无法收起歌词以换取更多列表空间。同时，歌词入库时 `original_filename` 可能沿用上传文件名或侧车原名，与当前试听/主音频文件名不一致，导致后台展示、对象键 stem 与本地侧车约定 `{audio_stem}.lrc` 脱节，增加运维与排查成本。

## What Changes

- **歌词显示切换**：为播放器「词」按钮绑定点击行为，切换第二行歌词区域（`.studio-player-row--lyrics`）的显示/隐藏；隐藏时播放器高度收缩，主内容区底部留白同步调整；按钮在开启态应有视觉反馈（如 `aria-pressed` / 激活类）。
- **默认与持久化**：歌词行默认显示（与当前行为一致）；切换状态可在会话内保存在 `localStorage`（可选，实现阶段在 design 中定夺）。
- **歌词文件名对齐音频**：入库（扫描侧车、后台上传替换）时，歌词 `SongFile.original_filename` SHALL 规范为「当前歌曲主音频文件名 stem + `.lrc`」，而非任意上传名；对象键 stem 随之与音频一致。
- **主音频选取规则**：以歌曲下可试听音频中择轨优先级最高的一条（与试听 API 一致）作为命名参照；若无音频则回退到已有任意音频文件的 `original_filename` stem。
- **范围外**：全屏歌词页、后台播放器歌词切换、已有 LRC 记录的批量迁移脚本（除非 design 中明确一次性搬迁）。

## Capabilities

### New Capabilities

（无 — 本次为既有歌词与前台播放器行为的优化。）

### Modified Capabilities

- `web-static-client-shells`：新增「词」按钮切换歌词行显示/隐藏及播放器高度联动要求。
- `song-lyrics`：新增歌词入库时 `original_filename` 须与主音频文件名 stem 对齐的要求。

## Impact

- **前端**：`app/static/index.html`（为歌词按钮增加稳定 `id`）、`app/static/frontend.js`（切换状态与 DOM/CSS 类）、`app/static/studio.css`（隐藏态高度、按钮激活态、主内容 `padding-bottom` 联动）。
- **后端**：`app/services.py`（`ingest_lyric_file` / 侧车关联时推导规范文件名；必要时 `relocate` 更新 object_key）、`app/main.py`（上传端点传参不变，内部命名由服务层统一）。
- **规范**：`web-static-client-shells`、`song-lyrics` 增量 spec。
- **不受影响**：歌词 API 契约、LRC 解析、检查器歌词 Tab、试听择轨逻辑（除命名参照只读复用）。
