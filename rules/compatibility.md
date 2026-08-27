---
purpose: 兼容性规范
content: 浏览器、SQLite、MinIO 和历史数据兼容约束
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# 兼容性规范

- UI 以现代 Chromium 浏览器为主要验证目标。
- SQLite 结构变更必须兼容已有 `data/music.db`。
- MinIO endpoint 在 Docker 与浏览器中可能不同，需同时考虑服务端和前端访问。
- 历史双桶对象迁移到单桶时必须先 dry-run。
