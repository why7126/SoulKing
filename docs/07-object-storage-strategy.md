---
purpose: 对象存储策略
content: ProjectSoulKing MinIO 单桶、对象键、迁移和签名 URL 约束
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 对象存储策略

ProjectSoulKing 使用并列 `ProjectMinio` 的 MinIO 服务，当前采用单桶 `soulking`。

## Bucket 与前缀

| 类型 | Bucket | 前缀 / 键规则 |
|---|---|---|
| 音频与歌词 | `soulking` | `music/{原唱1&原唱2}/{歌曲名}/{文件名}.{格式}` |
| 头像 / 图片 | `soulking` | `covers/` 前缀 |

路径段必须清洗非法字符；对象键全局冲突时追加哈希后缀。歌曲重命名、文件重命名、批量更新或合并后，如影响路径语义，应通过后端执行 copy + delete 的对象迁移。

## 签名 URL

- 浏览器可见资源应使用后端生成的 presigned URL。
- 前端不得自行给 presigned URL 追加未签名查询参数。
- Docker 运行时建议设置 `S3_PUBLIC_ENDPOINT_URL=http://127.0.0.1:9000`，避免浏览器访问 `host.docker.internal` 失败。

## 单桶迁移

历史 `music-files` / `music-covers` 迁移到 `soulking` 时使用：

```bash
python scripts/migrate_minio_to_soulking.py --dry-run
python scripts/migrate_minio_to_soulking.py
python scripts/migrate_minio_to_soulking.py --delete-old-buckets
```

## 验收与升级证据

媒体相关变更或发布检查 SHOULD 引用 [standards/media-asset-acceptance-template.md](standards/media-asset-acceptance-template.md)，按 key、object、URL / playback、metadata、UI render 五维记录音频、歌词、封面和头像链路证据。

版本升级计划涉及对象存储时，必须记录：

- 受影响媒体类型和脱敏对象 key 摘要。
- 对象存在性、MIME、size 或访问权限摘要。
- presigned URL、后端流式接口或下载接口 smoke 结果。
- 对象键迁移、copy + delete 或写入型维护任务的 dry-run / apply 边界。
- 回滚依赖的对象备份、旧 key 摘要或人工恢复方案。

证据不得包含真实密钥、完整私有对象 URL、Authorization header、Cookie、`.env` 内容、本机绝对路径或个人媒体内容。
