---
purpose: 生产部署矩阵说明
content: ProjectSoulKing 生产 SQLite + 外部 MinIO/S3 兼容部署方式
created_at: 2026-08-04 00:00:00
updated_at: 2026-08-04 00:00:00
---

# Production Deploy

当前生产矩阵为 `prod sqlite-minio-external`，匹配 ProjectSoulKing 现有代码能力：FastAPI + SQLite 持久化卷 + 外部 MinIO/S3 兼容对象存储。

```bash
cp deploy/prod/sqlite-minio-external.env.example deploy/prod/sqlite-minio-external.env
# 修改真实生产密钥、数据库路径、对象存储 endpoint、bucket 和端口后再启动
bash deploy/scripts/up.sh prod sqlite-minio-external
```

生产要求：

- `APP_ENV=production`
- `APP_DEBUG=false`
- `DATABASE_URL` 使用容器内持久化 SQLite 路径，例如 `sqlite:////data/music.db`
- 对象存储必须为外部服务，生产 Compose 不启动 MinIO
- `ADMIN_PASSWORD`、`S3_ACCESS_KEY_ID`、`S3_SECRET_ACCESS_KEY` 必须替换示例值
- 产品手册站只挂载 `mintlify/`，不得挂载真实 env、数据库或媒体目录
