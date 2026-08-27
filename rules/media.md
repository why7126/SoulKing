---
purpose: 媒体规范
content: 音频、歌词、头像和本地导入数据的处理边界
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 媒体规范

- 音频导入源为 `import/`，不得提交个人媒体文件。
- 同内容音频以 `sha256 + file_size` 识别，历史重复歌曲按既有合并策略处理。
- 删除、合并、重命名音频文件时必须说明是否删除对象存储实体。
- 头像上传需校验文件类型、大小和签名 URL 展示链路。
- 媒体相关 REQ、BUG、OpenSpec Change、Sprint 验收或 release 检查 SHOULD 使用 `docs/standards/media-asset-acceptance-template.md` 记录 key、object、URL / playback、metadata、UI render 五维证据。
