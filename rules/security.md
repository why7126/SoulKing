---
purpose: 安全规范
content: 登录、管理员保护、密钥、Cookie 和对象存储安全要求
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 安全规范

- 除 `/login`、`POST /auth/login`、`GET /health` 和静态资源外，业务 API 默认需要认证。
- 管理接口必须校验管理员角色。
- 密码必须哈希存储，不记录明文。
- `.env`、`.env.*`、`deploy/local/*.env`、`deploy/prod/*.env`、`scripts/build-images.env` 可作为本地真实环境文件存在，但必须被 `.gitignore` 覆盖且不得提交。
- 真实 env 内容、真实密钥、Authorization header、Cookie、数据库连接串和本机绝对路径不得写入 release、Mintlify、归档证据、AI Usage、命令输出或回复正文。
- presigned URL 只由后端生成，前端不得拼接绕过签名。
- 升级计划、根因证据和媒体验收记录只能写脱敏摘要；不得保存完整私有对象 URL、个人媒体内容、真实 `.env` 值或未脱敏日志。
