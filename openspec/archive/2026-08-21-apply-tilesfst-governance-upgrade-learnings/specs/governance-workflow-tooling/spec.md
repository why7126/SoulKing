## ADDED Requirements

### Requirement: 版本升级路径治理

本项目 MUST 支持以治理脚本和 Agent 技能记录 `from_version -> to_version` 的部署升级路径、支持级别、备份、回滚和 smoke 证据。

#### Scenario: 生成升级计划

- **WHEN** 用户运行 `/upgrade-plan --from <fresh|version> --to <version>`
- **THEN** 命令 MUST 生成或更新 `releases/<to-version>/upgrade-plans/<from>-to-<to>.json`
- **AND** 计划 MUST 记录目标 release、目标 image manifest、`SOULKING_IMAGE_TAG`、SQLite 备份要求、env diff、MinIO 对象存储影响、升级步骤、回滚步骤、blockers、warnings 和 evidence
- **AND** 命令 MUST NOT 自动执行生产升级、修改真实 env、恢复数据库或写入对象存储

#### Scenario: 校验升级计划

- **WHEN** 用户运行 `/upgrade-validate --plan <path>`
- **THEN** 命令 MUST 校验升级计划必填字段、支持级别、回滚块和公开安全边界
- **AND** 输出 MUST 只包含摘要、blocker/warning 和修复建议
- **AND** 不得输出真实 `.env` 值、密钥、数据库文件路径、Authorization header、Cookie 或本机绝对路径

### Requirement: 证据化根因分析

本项目 MUST 在问题排查、BUG 完善、BUG 来源实现和验收返修中区分根因证据强度，避免把推测包装成确认结论。

#### Scenario: 根因状态与证据链

- **WHEN** `root-cause.md` 或相关治理记录声明根因为 `confirmed`
- **THEN** 文档 MUST 记录可定位的脱敏证据链
- **AND** 证据链 SHOULD 包含复现、日志、测试、截图、配置差异、数据样本或代码定位等摘要

#### Scenario: 证据不足时保留不确定性

- **WHEN** 根因状态为 `unknown`、`hypothesis` 或 `probable`
- **THEN** 文档 MUST 说明仍需补充的证据或验证步骤
- **AND** 命令不得将该状态表述为已确认根因

### Requirement: 音乐媒体资产验收模板

本项目 MUST 为音频、歌词、封面、头像和对象存储相关变更提供统一的媒体资产验收记录口径。

#### Scenario: 媒体资产五维验收

- **WHEN** REQ、BUG、OpenSpec Change、Sprint 或 release 触达音乐媒体链路
- **THEN** 验收记录 SHOULD 按 `key`、`object`、`URL / playback`、`metadata`、`UI render` 五个维度记录结论
- **AND** 任一维度为 `fail` 或 `blocked` 时，整体结论不得写为 `pass`
- **AND** 记录不得包含真实密钥、访问令牌、完整私有对象 URL、未脱敏日志或本机绝对路径
