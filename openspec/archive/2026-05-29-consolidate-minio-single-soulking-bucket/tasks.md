## 1. MinIO 数据迁移

- [x] 1.1 新增 `scripts/migrate_minio_to_soulking.py`：复制 `music-files` → `soulking`（同键）、`music-covers` → `soulking`/`covers/` 前缀；支持 dry-run 与对象计数校验
- [x] 1.2 在本地 MinIO 上执行迁移脚本，确认 `soulking` 对象完整后删除 `music-files`、`music-covers` 桶
- [x] 1.3 在 README 中记录迁移顺序（先迁移、再改 `.env`、再启应用）及脚本用法

## 2. 应用配置与存储层

- [x] 2.1 `app/config.py`：默认 `s3_bucket_music` 改为 `soulking`；移除 `s3_bucket_covers`
- [x] 2.2 `app/storage.py`：`ensure_buckets` 仅创建/校验 `soulking` 单桶
- [x] 2.3 `.env.example`：更新 `S3_BUCKET_MUSIC=soulking`，删除 `S3_BUCKET_COVERS` 行
- [x] 2.4 更新开发者本地 `.env`（若存在旧桶名）并核对 `app/services.py` 中 `s3://` 诊断文案

## 3. 文档

- [x] 3.1 更新 `iterations/技术实现方案.md` 中对象存储章节为单桶 `soulking` 与前缀表
- [x] 3.2 确认 `packaging/mac/run_app.py` 默认环境变量与 README MinIO 说明一致

## 4. 验证

- [x] 4.1 重启应用后 `ensure_buckets_retry` 成功，仅存在 `soulking` 桶
- [x] 4.2 抽样验证：音频流式播放、歌词、头像上传与 `/auth/me` presigned URL
- [x] 4.3 `mc ls local/soulking/covers/`（或等价）确认原封面桶对象已迁入
