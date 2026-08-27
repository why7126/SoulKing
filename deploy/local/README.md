---
purpose: 本地部署矩阵说明
content: ProjectSoulKing 本地 SQLite + MinIO 环境启动方式
created_at: 2026-08-04 00:00:00
updated_at: 2026-08-04 00:00:00
---

# Local Deploy

本地矩阵统一使用 `deploy/local/compose.yml`：

- `sqlite-minio-external`：默认环境，连接并列 `ProjectMinio` 或其他外部 MinIO。
- `sqlite-minio-managed`：启用 `self-hosted-storage` profile，由本 Compose 启动 MinIO 并创建 `soulking` bucket。

```bash
bash deploy/scripts/up.sh local sqlite-minio-external
bash deploy/scripts/up.sh local sqlite-minio-managed
```

访问：

- 前台：`http://localhost:8000/`
- 后台：`http://localhost:8000/admin`
- 登录：`http://localhost:8000/login`
- API Docs：`http://localhost:8000/docs`
- 产品手册预览：`http://localhost:3001`
