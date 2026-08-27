---
purpose: OpenSpec 设计
content: TilesFST 治理学习项在 ProjectSoulKing 的项目化落地设计
created_at: 2026-08-21 22:50:52
updated_at: 2026-08-21 22:50:52
---

# 设计

## 设计原则

- 以 ProjectSoulKing 当前事实为准：FastAPI、SQLite、MinIO 单桶 `soulking`、静态 Web 壳和 `.agents/skills/`。
- 学习内容只迁移治理模式，不迁移 TilesFST 的业务名词、MySQL/COS、小程序或 SKU 验收语境。
- 长期规则只放在唯一归属文档；入口文档只写摘要和链接。
- 所有新增脚本默认只读或生成治理计划，禁止自动执行生产写入动作。

## 升级路径治理

新增脚本 `scripts/validate-release-upgrade.py`，提供：

- `plan --from <fresh|version> --to <version>`：读取目标 release、image manifest、env 示例和当前仓库事实，生成 `releases/<to-version>/upgrade-plans/<from>-to-<to>.json`。
- `validate-plan --plan <path>`：校验计划字段、支持级别、回滚块、敏感信息边界和 blocker/warning。
- `env-diff`：只比较 env 示例变量名和分类，不输出真实 env 值。

SoulKing 适配点：

- 镜像 tag 使用 `SOULKING_IMAGE_TAG`。
- 生产 DB 以 SQLite 数据文件为主，升级计划要求升级前备份 `data/` 中数据库文件、记录启动幂等迁移证据和升级后核心读写 smoke。
- 对象存储使用外部 MinIO/S3 单桶 `soulking`，升级计划关注对象键迁移、头像/封面/歌词/音频访问 smoke 和回滚边界。
- 首次部署、相邻升级、跨版本升级共用同一目标版本 image manifest，不为不同路径构建不同业务镜像。

## 根因证据治理

新增 `rules/root-cause-evidence.md` 作为 BUG、返修和问题排查根因证据事实源。状态集合：

- `unknown`
- `hypothesis`
- `probable`
- `confirmed`

新增脚本只校验文档契约：

- `confirmed` 必须包含可定位证据关键词。
- 未确认状态应包含补证或验证步骤。
- 不改写 BUG 文档，不推断根因。

## 媒体验收模板

新增 `docs/standards/media-asset-acceptance-template.md`，围绕音乐资产定义五维证据：

- `key`：对象键与歌曲、歌词、头像或封面资源关系。
- `object`：对象存储存在性、MIME、大小、权限。
- `URL / playback`：签名 URL、流式播放、下载或前端展示访问结果。
- `metadata`：音频指纹、格式、时长、歌词格式、封面尺寸等摘要。
- `UI render`：前台、后台、登录/用户资料等用户入口的可见状态。

模板只定义记录口径，不新增媒体处理能力。

## 文档索引

`docs/README.md` 仅补充 standards 分层和新增标准链接；详细规则仍归属各 `rules/` 或 `docs/standards/` 文件。

## 验证策略

- 脚本自测：运行新增脚本的 help、典型 plan、validate-plan 和 root-cause 校验样例。
- 治理校验：上下文预算、OpenSpec 语言、目录结构、目标 Change validate、Sprint scope、文档表达卫生。
- Workflow Sync：以 `opsx.apply` 同步本 Change 所在 Sprint，并运行 AI Usage hook。
