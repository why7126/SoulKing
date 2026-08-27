---
purpose: 兼容性矩阵
content: ProjectSoulKing 浏览器、数据库、对象存储和运行环境兼容范围
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# 兼容性矩阵

| 类型 | 当前目标 | 说明 |
|---|---|---|
| 浏览器 | Chromium 系浏览器 | 前后台静态壳以现代 DOM、CSS 和 fetch 为基础 |
| 后端运行时 | Python 3.12 | 依赖 FastAPI、SQLAlchemy、Pydantic、boto3 |
| 数据库 | SQLite | 私有化单实例 MVP 主库 |
| 对象存储 | MinIO S3 API | 由并列 `ProjectMinio` 提供 |
| 容器 | Docker Compose | 本仓库只启动 app，不启动 MinIO |
| 桌面封装 | macOS helper | `packaging/mac/` 保留本地封装辅助 |
