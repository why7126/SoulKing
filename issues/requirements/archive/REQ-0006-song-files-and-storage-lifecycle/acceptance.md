---
requirement_id: REQ-0006-song-files-and-storage-lifecycle
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
source: requirement.md
---

# 验收标准

- AC-001：向已有歌曲追加音频文件
- AC-002：修改展示用文件名并同步存储路径
- AC-003：删除单条音频文件
- AC-004：按歌曲同步存储路径
- AC-005：对象键的计算与全局唯一性
- AC-006：按文件标识流式读取与附件下载
- AC-007：向已有歌曲上传歌词文件
- AC-008：删除歌词文件记录
- AC-009：音频与歌词对象存储桶

## 通用验收
- [x] `openspec/specs/song-files-and-storage-lifecycle/spec.md` 已存在并作为已生效能力事实源。
- [x] 项目文档中保留该能力的产品、API、数据或存储说明（如适用）。
- [x] 本需求未引入新的代码行为变更。

## 测试策略
- 以 OpenSpec 中每个 Scenario 作为回归用例来源。
- 涉及 API 的能力通过 FastAPI `/docs`、接口调用或集成测试验证。
- 涉及 UI 的能力通过前后台静态壳手工或浏览器自动化验证。
- 涉及对象存储的能力需覆盖 MinIO 可用、对象缺失和路径迁移场景。

## Knowledge Gate

| 来源 | 适用性 | 写入位置 |
|---|---|---|
| `docs/knowledge-base/README.md` | not_applicable | 当前知识库无针对 `song-files-and-storage-lifecycle` 的专项条目 |
