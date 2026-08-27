---
purpose: OpenSpec 变更提案
content: 应用 TilesFST 的升级治理、根因证据、媒体验收和文档索引学习项
created_at: 2026-08-21 22:50:52
updated_at: 2026-08-21 22:50:52
---

# 应用 TilesFST 治理升级学习项

## 背景

`/spec-study TilesFST` Phase 1 确认 ProjectSoulKing 已吸收日志优先学习、文档表达卫生、review 默认通过、usage docs 和镜像发布治理等能力，但仍缺少三类可复用治理能力：

- 版本升级路径事实源：当前 release 与 image manifest 可表达目标版本事实，但无法表达 `from_version -> to_version` 的升级支持级别、备份、回滚和 smoke 证据。
- 证据化根因：BUG 完善已有根因要求，但未强制区分证据强度，confirmed 根因缺少轻量校验入口。
- SoulKing 媒体验收模板：音频、歌词、封面、头像和对象存储链路缺少统一的 key/object/URL/playback/metadata/UI 证据记录口径。

同时，`docs/README.md` 的 standards 索引较简，需要随本次新增标准同步补强。

## 变更内容

- 新增 `/upgrade-plan` 与 `/upgrade-validate` Agent 技能，配套新增 `scripts/validate-release-upgrade.py`。
- 在 release、environment、database、object storage、media、deployment 和 image release 文档中补充 SoulKing 版本升级路径治理。
- 新增 `rules/root-cause-evidence.md` 与 `scripts/validate-root-cause-evidence.py`，并同步 BUG、测试、explore、bug-complete、opsx-apply、opsx-modify、workflow-sync 入口。
- 新增 `docs/standards/media-asset-acceptance-template.md`，作为音乐媒体链路验收模板，并同步媒体和对象存储规则。
- 补强 `docs/README.md` standards 索引、`DOCUMENT_METADATA_INDEX.md`、目录结构和项目命令入口。
- 生成单份 `/spec-study` 学习报告并维护 `docs/spec-logs/CHANGELOG.md`。

## 不做内容

- 不修改业务运行时代码、API 路由、数据库模型、静态 Web 页面或桌面封装。
- 不执行真实生产升级、DB restore、对象存储写入维护或真实 env 修改。
- 不照搬 TilesFST 的 MySQL、COS、小程序、SKU、证书或瓷砖媒体规则。
- 不直接修改 `openspec/specs/`；正式规格更新留给归档阶段合并。

## 影响

- API：无运行时接口变更。
- 数据库：无 schema 变更；新增升级计划中的 SQLite 备份和迁移证据要求。
- 前台 Web / 后台管理端：无运行时变更；新增媒体验收证据模板。
- 桌面封装：无影响。
- 对象存储：无实现变更；新增升级和媒体验收证据口径。
- Docker Compose：无拓扑变更；新增升级计划校验对 Compose/env 示例的检查要求。
- 测试：新增治理脚本校验和脚本自测。
