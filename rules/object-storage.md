---
purpose: 对象存储规范
content: MinIO 单桶、对象键、签名 URL 和迁移规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 对象存储规范

- 当前只使用 `soulking` 单桶。
- 音频对象键遵循 `music/{artists}/{song}/{filename}.{ext}`，头像等图片使用 `covers/`。
- 对象键变化必须由后端执行 copy + delete，并同步数据库。
- 浏览器访问私有对象必须使用后端生成的 presigned URL 或后端流式接口。
- 跨桶迁移使用 `scripts/migrate_minio_to_soulking.py`。
- 升级计划或媒体链路验收涉及对象存储时，必须记录脱敏 object key、对象存在性、受控访问方式和回滚边界；不得记录完整私有对象 URL、AccessKey、SecretKey 或未脱敏日志。
