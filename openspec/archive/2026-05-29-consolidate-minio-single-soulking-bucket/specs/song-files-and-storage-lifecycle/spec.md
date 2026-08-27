## ADDED Requirements

### Requirement: 音频与歌词对象存储桶

本能力涉及的所有对象存储读写（上传、桶内复制、删除、presigned/流式 GET）SHALL 使用配置项 `s3_bucket_music` 所指定的桶；默认桶名为 `soulking`。对象键的计算与全局唯一性规则不变。

#### Scenario: 追加音频写入 soulking

- **GIVEN** 应用已配置 `S3_BUCKET_MUSIC=soulking` 且迁移已完成
- **WHEN** 客户端成功向歌曲追加音频文件
- **THEN** 对象存在于 `soulking` 桶中
- **AND** 键名符合现有分层路径规则

#### Scenario: 流式读取使用同一桶

- **GIVEN** 文件记录的 `object_key` 在迁移后仍指向 `soulking` 内有效对象
- **WHEN** 客户端请求流式播放接口
- **THEN** 从 `soulking` 桶按该键拉取对象
