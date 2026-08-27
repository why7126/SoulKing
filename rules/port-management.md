---
purpose: 端口规范
content: 本地端口、服务归属和冲突处理规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# 端口规范

| 服务 | 默认端口 |
|---|---:|
| ProjectSoulKing app | 8000 |
| ProjectMinio API | 9000 |
| ProjectMinio Console | 9001 |

端口变更必须同步 `.env.example`、`docker-compose.yml`、`docs/02-deployment.md` 和 README。
