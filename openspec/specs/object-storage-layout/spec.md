# object-storage-layout Specification

## Purpose

定义全项目唯一的 MinIO/S3 对象存储桶（默认 `soulking`）、桶内目录前缀（音频/歌词、头像、`covers/`）及自双桶架构迁移的存量数据要求。
## Requirements
### Requirement: 单一对象存储桶

系统 SHALL 仅使用一个 MinIO/S3 桶存储本项目全部对象；默认桶名为 `soulking`，可通过环境变量 `S3_BUCKET_MUSIC` 覆盖。系统 MUST NOT 再配置或创建第二个业务桶（原 `music-covers` 桶已废弃）。

#### Scenario: 应用启动确保桶存在

- **GIVEN** MinIO 可访问且 `S3_BUCKET_MUSIC` 为 `soulking`（或未设置而使用默认值）
- **WHEN** 应用启动并执行存储初始化
- **THEN** `soulking` 桶存在或已被创建
- **AND** 不会创建名为 `music-covers` 的桶

#### Scenario: 无封面专用桶配置

- **GIVEN** 部署环境仅提供 `S3_BUCKET_MUSIC`
- **WHEN** 加载应用配置
- **THEN** 不存在 `S3_BUCKET_COVERS` 或 `s3_bucket_covers` 配置项

### Requirement: 桶内目录前缀约定

`soulking` 桶内对象 SHALL 按下列前缀组织：

- 音频与歌词文件：使用现有 `object_key` 分层路径（桶根下，无强制额外前缀）。
- 用户头像：`avatar/{user_id}.{ext}`。
- 封面图片（自原 `music-covers` 桶迁入或今后上传）：`covers/` 前缀下；自 `music-covers` 迁移时，原对象键 `K` 对应新键 `covers/K`（若 `K` 已以 `covers/` 开头则保持为 `K`）。

#### Scenario: 封面对象位于 covers 前缀

- **GIVEN** 某封面对象自 `music-covers` 桶键 `album/1.jpg` 迁移完成
- **WHEN** 在 `soulking` 桶中查询
- **THEN** 对象键为 `covers/album/1.jpg`

#### Scenario: 音频对象键不因桶合并而改变

- **GIVEN** 迁移前音频对象在 `music-files` 桶键为 `Artist/Title/track.flac`
- **WHEN** 迁移至 `soulking` 完成
- **THEN** 对象键仍为 `Artist/Title/track.flac`
- **AND** 曲库中 `SongFile` 记录的 `object_key` 无需修改

### Requirement: MinIO 存量迁移

部署本变更的环境 MUST 在切换到 `soulking` 配置前，将 `music-files` 桶内全部对象复制到 `soulking`（相同键），并将 `music-covers` 桶内对象复制到 `soulking` 的 `covers/` 前缀下。迁移验证通过后 MUST 删除 `music-files` 与 `music-covers` 桶。

#### Scenario: 迁移后旧桶不存在

- **GIVEN** 迁移脚本或运维流程已按规范执行完毕
- **WHEN** 列出 MinIO 全部桶
- **THEN** 存在 `soulking`
- **AND** 不存在 `music-files` 与 `music-covers`

