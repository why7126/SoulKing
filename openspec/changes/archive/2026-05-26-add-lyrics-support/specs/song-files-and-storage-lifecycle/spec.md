## ADDED Requirements

### Requirement: 向已有歌曲上传歌词文件

除向歌曲追加音频文件外，客户端 MAY 通过歌曲歌词专用接口提交 `.lrc` 文件（见 `song-lyrics` 规格中的上传要求）。该路径 MUST NOT 使用音频追加接口的扩展名白名单校验；成功后不得改变歌曲的试听择轨结果。

#### Scenario: 歌词上传不改变音频变体列表语义

- **GIVEN** 歌曲下已有若干音频 `SongFile` 记录
- **WHEN** 客户端通过歌词上传接口成功提交 `.lrc`
- **THEN** 歌曲下音频记录数量与格式集合不变（除新增一条 `format=lrc` 外）
- **AND** 试听接口仍仅从可播放音频变体中择轨

### Requirement: 删除歌词文件记录

当客户端通过歌曲歌词删除接口移除歌词，或当系统因替换/合并执行 LRC 去重时，服务端 MUST 删除对应对象存储对象及 `SongFile` 记录。删除歌词 MUST NOT 删除该曲下的音频文件记录。

#### Scenario: 仅删除 LRC 保留音频

- **GIVEN** 歌曲下同时存在音频记录与 LRC 记录
- **WHEN** 客户端成功删除该曲歌词
- **THEN** 所有音频 `SongFile` 记录仍存在
- **AND** LRC 记录与对象均不存在
