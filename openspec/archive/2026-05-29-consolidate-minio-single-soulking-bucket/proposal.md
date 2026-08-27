## Why

当前 MinIO 使用 `music-files` 与 `music-covers` 两个桶，增加运维与配置复杂度，且封面桶尚未与业务代码深度集成。产品要求全项目仅保留一个对象存储桶，统一命名与目录前缀，便于备份、权限与后续封面等功能在同一桶内演进。

## What Changes

- **BREAKING**：默认桶名由 `music-files` 改为 `soulking`；环境变量 `S3_BUCKET_MUSIC` 默认值同步更新。
- 移除 `music-covers` 桶及配置项 `S3_BUCKET_COVERS` / `s3_bucket_covers`；应用启动时仅确保 `soulking` 桶存在。
- 在 MinIO 上执行数据迁移：`music-files` 桶内对象迁至 `soulking`（同键或按设计保持键不变）；`music-covers` 桶内对象迁至 `soulking` 桶下 `covers/` 前缀目录。
- 迁移完成后删除 MinIO 上的 `music-files` 与 `music-covers` 桶（空桶或确认无残留后）。
- 更新文档（`.env.example`、`README.md`、相关 OpenSpec 规格）中的桶名与单桶布局说明。
- 提供可重复执行的迁移脚本或文档化步骤（mc / boto3），供开发与生产环境使用。

## Capabilities

### New Capabilities

- `object-storage-layout`：定义全项目唯一的 `soulking` 桶、各业务前缀（音频、歌词、头像、`covers/` 等）及配置约定。

### Modified Capabilities

- `application-auth`：头像 presigned URL 所引用的桶名由 `music-files` 改为 `soulking`。
- `user-self-service`：头像上传目标桶由 `music-files` 改为 `soulking`。
- `song-files-and-storage-lifecycle`：明确所有音频/歌词对象均存于 `soulking` 桶（键规则不变，仅桶名变更）。

## Impact

- `app/config.py`、`app/storage.py`：单桶配置与 `ensure_buckets` 逻辑。
- `.env` / `.env.example`：移除 `S3_BUCKET_COVERS`，更新 `S3_BUCKET_MUSIC` 默认值。
- `app/services.py`：错误信息中的 `s3://` URI 桶名。
- `README.md`、`iterations/技术实现方案.md`（若仍描述双桶）。
- 运行中的 MinIO 实例：需执行桶重命名/对象复制与旧桶清理；已有 presigned URL 与外部书签在迁移窗口内会失效。
- OpenSpec 主规格：`application-auth`、`user-self-service`、`song-files-and-storage-lifecycle` 及新建 `object-storage-layout`。
