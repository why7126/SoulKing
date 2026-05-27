## Why

后台编辑歌曲保存时，修改歌名后音频与歌词在管理端的展示文件名（`original_filename`）仍保留旧名，对象存储路径中的文件名段也与新歌名不一致，造成元数据、文件列表与存储布局脱节。同时，编辑抽屉中的「时长」字段为只读展示，用户无法手动修正从标签读取错误或缺失的时长。

## What Changes

- **服务端**：在 `PUT /songs/{id}` 中，当请求修改了歌曲标题且与旧标题不同时，将该曲下所有音频与歌词文件的 `original_filename` 统一更新为 `{sanitize(新标题)}.{扩展名}`（规则 1），随后执行已有的 `relocate_song_files_storage` 搬迁对象存储路径。
- **管理端 UI**：编辑抽屉「时长」字段改为可编辑，以 `mm:ss` 格式展示与输入（如 `03:45`），保存时解析为 `duration_ms` 提交 API；非法格式阻止保存并提示用户。
- **时长语义**：输入留空表示清空时长（`null`）；`00:00` 表示 0 毫秒。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `song-catalog-and-metadata`：更新歌曲元数据时，若标题发生变更，须同步更新关联音频与歌词文件的展示名，再调整对象存储路径。
- `web-static-client-shells`：后台编辑抽屉的时长字段须可编辑，并以 `mm:ss` 格式约束输入与校验。

## Impact

- **后端**：`app/services.py`（新增 title 联动重命名辅助函数）、`app/main.py`（`update_song` 在 flush 前调用）、可能涉及 `song-lyrics` 相关 ingest 命名逻辑复用。
- **前端**：`app/static/admin.html`（移除时长只读）、`app/static/admin.js`（`parseDurationMmSs` / 校验 / 保存逻辑）。
- **规范**：`openspec/specs/song-catalog-and-metadata/spec.md`、`openspec/specs/web-static-client-shells/spec.md` 增量。
- **API**：`PUT /songs/{id}` 行为扩展（非破坏性）；请求/响应 schema 不变。
