---
purpose: API 索引
content: ProjectSoulKing REST API 分组和同步要求
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# API 索引

FastAPI 运行后以 `http://localhost:8000/docs` 为交互式事实入口。新增或修改 API 时必须同步 OpenSpec、本文档和相关前端调用。

| 分组 | 代表接口 | 职责 |
|---|---|---|
| Health | `GET /health` | 服务健康检查 |
| Auth | `POST /auth/login`、`POST /auth/logout`、`GET /auth/me` | 登录、退出、当前用户、自助资料和密码 |
| Library | `POST /libraries/scan` | 扫描 `import/` 并导入音乐 |
| Songs | `GET /songs`、`GET /songs/{song_id}` | 曲库查询、详情、筛选 |
| Song files | `GET /song-files/{id}/stream`、`GET /song-files/{id}/download` | 音频播放、下载、文件级操作 |
| Playlists | `GET /playlists` 等 | 歌单管理 |
| Admin | `/admin/*` | 后台歌曲、参考数据、用户、批量治理 |

API 响应结构应保持前端兼容；涉及认证、管理员权限或对象存储签名 URL 的变更必须补充安全说明。
