---
purpose: 部署矩阵入口
content: ProjectSoulKing 本地、生产和产品手册站部署入口
created_at: 2026-08-04 00:00:00
updated_at: 2026-08-07 13:04:31
---

# Deploy Matrix

`deploy/` 承载 ProjectSoulKing 的可执行部署矩阵。根目录 `docker-compose.yml` 保留兼容入口；新增环境优先使用本目录脚本，以便统一 env 校验、Compose profile、端口和产品手册站部署。

原则：

- 一拓扑一 Compose；服务拓扑变化才新增 Compose 或 profile。
- 一环境一 env 示例；变量差异通过 `*.env.example` 表达。
- 脚本集中到 `deploy/scripts/`；根 `scripts/docker-up.sh` 与 `scripts/docker-down.sh` 只保留兼容 wrapper。
- 改动根 `docker-compose.yml` 后，同步检查 `deploy/local/compose.yml`、`docs/02-deployment.md`、`deploy/local/README.md` 和 `.env.example`。
- 只提交示例配置；真实 env、密钥、数据库连接串、运行时数据库、MinIO 数据和镜像包不得进入仓库。

## 环境

| 环境 | Compose | Env example | 对象存储 | 用途 |
|---|---|---|---|---|
| `local sqlite-minio-external` | `deploy/local/compose.yml` | `deploy/local/sqlite-minio-external.env.example` | 并列 `ProjectMinio` 或外部 MinIO | 默认本地开发 |
| `local sqlite-minio-managed` | `deploy/local/compose.yml` | `deploy/local/sqlite-minio-managed.env.example` | Compose 内托管 MinIO | 独立本地演示 |
| `prod sqlite-minio-external` | `deploy/prod/compose.sqlite-minio-external.yml` | `deploy/prod/sqlite-minio-external.env.example` | 外部 MinIO/S3 兼容服务 | 私有化生产部署 |

## 命令

```bash
bash deploy/scripts/up.sh local sqlite-minio-external
bash deploy/scripts/up.sh local sqlite-minio-managed
bash deploy/scripts/up.sh prod sqlite-minio-external

bash deploy/scripts/down.sh local
bash deploy/scripts/down.sh prod
```

脚本会优先读取 `deploy/<domain>/<environment>.env`；不存在时退回对应 `.env.example` 用于 `docker compose config` 或本地试运行。真实 env 文件禁止提交。

本地可保留 `.env`、`.env.*`、`deploy/local/*.env`、`deploy/prod/*.env` 和 `scripts/build-images.env`。这些文件被 `.gitignore` 覆盖且不应被 Git 跟踪；只要未进入仓库、release、Mintlify 或归档证据，它们的存在不阻断归档。

## 产品手册站

local 和 prod 矩阵均包含 `docs-site` profile，默认挂载 `mintlify/` 并通过静态预览服务暴露：

- 默认地址：`http://localhost:3001`
- 端口变量：`HOST_PORT_MINTLIFY_DOCS`
- 源目录：`mintlify/`
- 事实源：`releases/<version>/usage-docs/manifest.json`

生成和校验手册使用：

```bash
python scripts/generate-usage-docs.py <version>
python scripts/validate-usage-docs.py --release-dir releases/<version>
python scripts/validate-mintlify-site.py
```
