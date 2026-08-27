## ADDED Requirements

### Requirement: 数据采集治理学习应用

Agent 治理命令 SHALL 能通过 `/spec-study apply` 将外部项目的数据采集治理经验项目化应用到 SoulKing 的规则、技能、标准文档和校验脚本中。

#### Scenario: 数据采集治理项目化改写

- **GIVEN** 用户确认应用 TilesFST 数据采集学习项
- **WHEN** `/spec-study apply TilesFST --items D1,D2,D3,D4` 修改治理资产
- **THEN** 变更 SHALL 通过 active OpenSpec Change 和 Sprint scope 承载
- **AND** 学习对象 SHALL 保持只读
- **AND** 本项目 SHALL 生成单份 `docs/spec-logs/YYYYMMDDhhmmss-study-tilesfst-data-collection.md` 学习报告
- **AND** 应用内容 SHALL 使用 SoulKing 音乐资产、SQLite、MinIO、前台 Web、后台管理端和 `.agents/skills/` 语境重写
