---
purpose: 架构说明
content: ProjectSoulKing 服务组成、模块边界、数据流和存储边界
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# 架构说明

## 服务组成

| 层 | 位置 | 职责 |
|---|---|---|
| HTTP/API | `app/main.py`、`app/auth_routes.py` | FastAPI 路由、静态文件挂载、认证接口 |
| 业务服务 | `app/services.py`、`app/song_merge.py` | 扫描导入、元数据治理、重复歌曲合并 |
| 数据模型 | `app/models.py`、`app/schemas.py`、`app/database.py` | SQLAlchemy 表、Pydantic DTO、SQLite 会话 |
| 认证安全 | `app/auth.py`、`app/middleware_auth.py` | 密码哈希、会话 Cookie、受保护路由 |
| 对象存储 | `app/storage.py` | MinIO/S3 客户端、Bucket、对象键、签名 URL |
| Web 前台 | `app/static/index.html`、`frontend.js`、`studio.css` | 曲库、播放、歌单、用户自助 |
| Web 后台 | `app/static/admin.html`、`admin.js`、`admin-studio.css` | 音乐、参考数据和用户管理 |

## 数据流

1. 用户将音频放入 `import/`。
2. `POST /libraries/scan` 解析音频，计算内容指纹，写入 SQLite。
3. 音频写入 ProjectMinio 的 `soulking` 桶，路径按歌曲和艺人生成。
4. 前台和后台通过 REST API 读取歌曲、文件、歌词、歌单和用户信息。
5. 播放、下载、头像显示通过后端生成的私有签名 URL 或流式接口完成。

## 架构约束

- 根目录现有 `app/` 是当前源码边界，迁移到 `src/` 需单独 OpenSpec Change。
- 对象存储不由本仓库 compose 启动，必须依赖并列 `ProjectMinio`。
- `data/` 和 `import/` 是本地运行目录，不提交真实运行时数据或个人媒体。
