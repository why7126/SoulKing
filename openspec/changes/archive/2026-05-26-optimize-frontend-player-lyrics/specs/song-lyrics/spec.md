## ADDED Requirements

### Requirement: 歌词文件名与主音频对齐

当 LRC 通过目录扫描侧车关联或后台上传/替换写入曲库时，系统 SHALL 将歌词 `SongFile.original_filename` 设置为 `{主音频文件名 stem}.lrc`，其中「主音频」指该歌曲下按现有试听择轨规则（`choose_best_file` 同等优先级）选出的那条音频文件的 `original_filename`；若歌曲尚无任何音频文件，则 MAY 使用 `lyrics.lrc` 作为回退名。

入库流程 MUST NOT 将上传请求的原始文件名或侧车磁盘文件名原样作为最终 `original_filename`（除非其与上述推导结果一致）。对象键 MUST 基于规范化后的 `original_filename` 按现有 `compute_music_object_key` 规则生成。

#### Scenario: 侧车入库时文件名对齐

- **GIVEN** 歌曲 S 已成功入库音频文件 `MySong.flac`
- **WHEN** 扫描在同目录发现侧车 `other-name.lrc` 并关联到 S
- **THEN** 写入的 LRC 记录 `original_filename` 为 `MySong.lrc`
- **AND** 对象键路径段中的文件名为 `MySong.lrc`（或经 sanitize 后的等价形式）

#### Scenario: 后台上传替换时文件名对齐

- **GIVEN** 歌曲 S 存在主音频 `track-01.mp3`
- **WHEN** 客户端上传名为 `custom.lrc` 的文件替换歌词
- **THEN** 成功后 LRC 记录 `original_filename` 为 `track-01.lrc`
- **AND** 歌词读取 API 返回的 `filename` 字段为 `track-01.lrc`

#### Scenario: 无音频时的回退名

- **GIVEN** 歌曲 S 存在但尚无任何音频 `SongFile`
- **WHEN** 客户端为 S 上传 LRC
- **THEN** LRC 记录 `original_filename` 为 `lyrics.lrc`（或实现文档固定的等价回退名）

#### Scenario: 多音频时与试听择轨一致

- **GIVEN** 歌曲 S 同时存在 `a.flac` 与 `b.mp3`，且按格式优先级择轨选中 `a.flac`
- **WHEN** 为 S 关联或上传 LRC
- **THEN** LRC 的 `original_filename` 为 `a.lrc`
