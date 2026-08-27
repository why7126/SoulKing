---
purpose: OpenSpec 测试映射
content: 能力模块到验证方式的映射
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# 测试映射

| 能力 | 建议验证 |
|---|---|
| `application-auth` | 登录、退出、受保护 API、管理员权限、密码修改 |
| `music-ingestion` | `POST /libraries/scan`、重复导入、元数据解析 |
| `song-catalog-and-metadata` | 前后台列表、搜索、筛选、编辑、批量更新 |
| `song-files-and-storage-lifecycle` | 上传、重命名、删除、存储路径同步 |
| `audio-playback-and-download` | 播放、下载、格式优先级 |
| `object-storage-layout` | 单桶前缀、presigned URL、迁移脚本 dry-run |
| `playlist-management` | 歌单增删改查和歌曲关联 |
| `web-static-client-shells` | 前台、后台、登录页布局和关键交互 |
