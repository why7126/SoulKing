---
purpose: 部署说明
content: ProjectSoulKing 本地启动、Docker Compose、环境变量和端口约束
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 部署说明

## 部署入口

ProjectSoulKing 保留根 `docker-compose.yml` 作为兼容入口；标准部署矩阵位于 `deploy/`：

```bash
bash deploy/scripts/up.sh local sqlite-minio-external
bash deploy/scripts/up.sh local sqlite-minio-managed
bash deploy/scripts/up.sh prod sqlite-minio-external
```

`deploy/scripts/up.sh` 会先运行 `deploy/scripts/validate-env.py`，再按环境选择 Compose、env 文件和 profile。真实 env 文件为 `deploy/local/*.env` 或 `deploy/prod/*.env`，禁止提交；示例值只用于本地试运行和 `docker compose config`。

部署矩阵原则：

- 一拓扑一 Compose：服务拓扑变化才新增 Compose 或 profile。
- 一环境一 env 示例：变量差异通过 `*.env.example` 表达。
- 脚本集中：`deploy/scripts/` 负责环境解析、校验、up/down；根 `scripts/docker-up.sh` 与 `scripts/docker-down.sh` 只做 wrapper。
- 本地基线同步：改动根 `docker-compose.yml` 后，同步检查 `deploy/local/compose.yml`、`docs/02-deployment.md`、`deploy/local/README.md` 和 `.env.example`。
- 安全优先：只提交 `.env.example`，不得提交真实 `.env`、密钥、数据库连接串、个人媒体、运行时数据库、MinIO 数据或镜像包。

根目录 `.env` / `.env.*`、部署 env 和 `scripts/build-images.env` 允许作为本地真实配置存在，只要保持未被 Git 跟踪即可。它们的存在不阻断 OpenSpec、Sprint 或发布归档；归档和发布证据只记录示例文件、校验命令和脱敏摘要，不记录真实值。

## 本地 Docker 启动

ProjectSoulKing 依赖并列项目 `ProjectMinio` 提供对象存储：

```bash
cd ../ProjectMinio
docker compose -f docker-compose.yaml -p minio up -d
```

回到本仓库：

```bash
cp .env.example .env
docker compose up --build
```

或使用部署矩阵默认本地环境：

```bash
bash deploy/scripts/up.sh local sqlite-minio-external
```

访问：

- 前台：`http://localhost:8000/`
- 后台：`http://localhost:8000/admin`
- 登录：`http://localhost:8000/login`
- API 文档：`http://localhost:8000/docs`

## 端口

| 服务 | 默认端口 | 来源 |
|---|---:|---|
| FastAPI app | 8000 | 本仓库 `docker-compose.yml` |
| MinIO API | 9000 | `../ProjectMinio` |
| MinIO Console | 9001 | `../ProjectMinio` |
| 产品手册预览 | 3001 | `deploy/*/compose*.yml` 的 `docs-site` profile |

## 关键环境变量

| 变量 | 用途 |
|---|---|
| `DATABASE_URL` | Docker 中使用 `sqlite:////data/music.db`，本机直跑可用 `sqlite:///./data/music.db` |
| `S3_ENDPOINT_URL` | Docker 中通常为 `http://host.docker.internal:9000` |
| `S3_PUBLIC_ENDPOINT_URL` | 浏览器访问签名资源时建议为 `http://127.0.0.1:9000` |
| `S3_BUCKET_MUSIC` | 当前单桶默认 `soulking` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | 空库首次启动的管理员种子账号 |

## 生产部署

生产环境当前采用 `prod sqlite-minio-external`：

- FastAPI 应用容器：`deploy/prod/compose.sqlite-minio-external.yml`
- SQLite 数据：挂载到 `data/`，生产升级前必须备份
- 对象存储：外部 MinIO/S3 兼容服务
- 产品手册站：`docs-site` profile 只读挂载 `mintlify/`

```bash
cp deploy/prod/sqlite-minio-external.env.example deploy/prod/sqlite-minio-external.env
# 替换真实密钥、对象存储 endpoint、bucket、端口和镜像 tag
bash deploy/scripts/up.sh prod sqlite-minio-external
```

生产 env 必须满足：

- `APP_ENV=production`
- `APP_DEBUG=false`
- `S3_SECURE=true`
- `ADMIN_PASSWORD`、`S3_ACCESS_KEY_ID`、`S3_SECRET_ACCESS_KEY` 不得使用示例值
- 不在 `release.json`、`announcement.mdx`、`mintlify/` 或日志中写入真实 env 内容

## 版本升级计划

正式部署或升级前 SHOULD 生成版本升级计划：

```bash
python scripts/validate-release-upgrade.py plan --from fresh --to vX.Y.Z
python scripts/validate-release-upgrade.py plan --from vA.B.C --to vX.Y.Z
python scripts/validate-release-upgrade.py validate-plan --plan releases/vX.Y.Z/upgrade-plans/vA.B.C-to-vX.Y.Z.json
```

升级计划位于 `releases/<to-version>/upgrade-plans/`，用于区分：

- 首次部署：`fresh -> <to-version>`，重点校验目标 release、目标镜像、生产 env、SQLite 空库初始化、对象存储配置、Compose config 和部署后 smoke。
- 相邻升级：`<previous-version> -> <to-version>`，重点校验 env diff、`SOULKING_IMAGE_TAG` 切换、SQLite 备份、启动兼容迁移、重启和升级后 smoke。
- 跨版本升级：`<old-version> -> <to-version>`，必须聚合中间版本 DB、env、Docker、API、对象存储和维护任务影响；缺少演练或证据时标记为 `cross-version-upgrade-requires-manual-review` 或 `unsupported`。

三类部署均复用同一目标版本业务镜像，不为首次部署、相邻升级或跨版本升级分别构建不同镜像。回滚前必须确认旧镜像、旧 env 摘要、SQLite 备份、对象存储影响和回滚后 smoke；DB 回滚不得脱离备份恢复或已验证反向迁移策略。

## 产品手册站部署

产品手册由 release 快照生成：

```bash
python scripts/generate-usage-docs.py <version>
python scripts/validate-usage-docs.py --release-dir releases/<version>
python scripts/validate-mintlify-site.py
```

生成后会同步：

- `releases/<version>/usage-docs/`：版本事实源
- `mintlify/docs/<version>/`：版本站点页面
- `mintlify/docs/latest/`：latest 投影
- `mintlify/releases/<version>/announcement.mdx`：公告投影
- `mintlify/docs.json`、`mintlify/site-manifest.json`：导航与投影索引

本地或生产预览：

```bash
bash deploy/scripts/up.sh local sqlite-minio-external
# 或
bash deploy/scripts/up.sh prod sqlite-minio-external
```

访问 `http://localhost:3001` 检查站点源目录是否挂载成功。若需要对接 Mintlify 云端或静态 CDN，应以 `mintlify/` 为公开源目录，以 `releases/<version>/usage-docs/manifest.json` 为版本事实源。
