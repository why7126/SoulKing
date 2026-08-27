---
title: 生产镜像包构建与部署手册
purpose: 记录 ProjectSoulKing 的生产镜像构建、离线交付和服务器部署规范
created_at: 2026-07-31 00:00:00
updated_at: 2026-08-21 22:50:52
owner: 项目团队
status: draft
---

# 生产镜像包构建与部署手册

ProjectSoulKing 当前采用单 FastAPI 应用镜像承载后端 API 与 `app/static/` 静态 Web 壳。生产部署由 Docker Compose 启动 app，SQLite 数据位于 `data/`，对象存储使用外部 MinIO / S3 兼容服务。

## 1. 发布治理命令

正式发布涉及后端运行代码、静态 Web 壳、Dockerfile、Compose、构建脚本、构建 env、数据库模型/兼容迁移、API 文档或离线镜像交付时，必须把镜像证据纳入 `releases/<version>/`。

推荐顺序：

```text
/release-propose <version>
  -> /release-prepare <version>
  -> /image-prepare <version>
  -> /image-build <version>
  -> /release-publish <version>
```

`/image-prepare <version>` 生成：

```text
releases/<version>/image-build-plan.json
```

`/image-build <version>` 生成：

```text
releases/<version>/image-manifest.json
```

真实离线镜像包和 `.sha256` 默认输出到：

```text
releases/<version>/images/
```

## 2. 构建配置

可提交的示例配置为：

```text
scripts/build-images.env.example
```

真实构建配置为：

```text
scripts/build-images.env
```

`scripts/build-images.env` 不得提交。常规情况下由 `/image-prepare <version>` 从示例创建并把 `IMAGE_BUILD_TAG` 对齐到发布版本。

关键变量：

```env
IMAGE_BUILD_TAG=v0.0.1
IMAGE_BUILD_PLATFORM=linux/amd64
BACKEND_PYTHON_BASE_IMAGE=python:3.12-slim
IMAGE_BUILD_APP_IMAGE=soulking-app
IMAGE_BUILD_BUILDER=soulking-builder
IMAGE_BUILD_EXPORT_TAR=true
```

## 3. 构建流程

脚本化构建：

```bash
./scripts/build-images.sh
```

指定 env 文件：

```bash
./scripts/build-images.sh /path/to/build-images.env
```

脚本会执行：

1. 检查 Docker、gzip 与 buildx。
2. 创建或复用 `IMAGE_BUILD_BUILDER`。
3. 基于根目录 `Dockerfile` 构建 `IMAGE_BUILD_APP_IMAGE:IMAGE_BUILD_TAG`。
4. 验证镜像平台。
5. 验证应用依赖可导入 `fastapi`、`sqlalchemy`、`minio`。
6. 当 `IMAGE_BUILD_EXPORT_TAR=true` 时导出 gzip 离线镜像包并生成 `.sha256`。

## 4. 证据要求

`image-build-plan.json` 必须记录：

- release 稳定输入 hash。
- `Dockerfile`、Compose、构建脚本、构建 env 示例、数据库文档和模型文件的 input hash。
- 构建 env 安全摘要。
- warnings、blockers 和 auto_actions。

`image-manifest.json` 必须记录：

- version、image tag、platform。
- app image name/ref。
- tarball path、sha256、存在性。
- source plan path 与 sha256。
- 与 plan 一致的 input_hashes。

## 4.1 升级路径中的镜像证据

部署升级计划不重新定义镜像构建策略。首次部署、相邻升级和跨版本升级均引用目标版本同一份：

```text
releases/<version>/image-manifest.json
```

升级计划生成和校验时必须确认目标 manifest 存在、版本和 image tag 与目标版本一致，并能追溯镜像、离线包和 sha256。若 manifest 缺失、版本不一致、tag 不一致或 input hash 已漂移，升级计划必须输出 blocker。

样例命令：

```bash
python scripts/validate-release-upgrade.py plan --from v1.0.0 --to v1.1.0
python scripts/validate-release-upgrade.py validate-plan --plan releases/v1.1.0/upgrade-plans/v1.0.0-to-v1.1.0.json
```

回滚时使用旧版本镜像 tag、旧离线包或旧 manifest 作为恢复依据；SQLite 和对象存储回滚必须另行依赖备份或明确人工方案。

## 5. 部署边界

生产服务器部署前必须准备：

- 通过 `.sha256` 校验离线镜像包。
- `docker load -i images/<tarball>.tar.gz` 导入镜像。
- 从 `.env.example` 创建服务器本地 `.env`，填入真实密钥和外部 MinIO 配置。
- 备份 SQLite 数据目录或确认可回滚策略。
- 运行 `docker compose config --quiet` 与核心 smoke。

不得把真实 `.env`、数据库文件、MinIO 密钥、Authorization header、Cookie 或本机绝对路径写入 release artifact。
