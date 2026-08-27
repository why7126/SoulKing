---
requirement_id: REQ-0004-music-ingestion
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
source: requirement.md
---

# 验收标准

- AC-001：目录扫描入口与路径校验
- AC-002：上传文件入库入口
- AC-003：音频格式白名单
- AC-004：按内容去重
- AC-005：单文件入库管线
- AC-006：入库时歌曲标题与文件名
- AC-007：主艺人关联范围
- AC-008：目录扫描的任务记录与统计
- AC-009：进程内进度与重置
- AC-010：目录扫描的同步执行
- AC-011：目录扫描时关联侧车 LRC 文件

## 通用验收
- [x] `openspec/specs/music-ingestion/spec.md` 已存在并作为已生效能力事实源。
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
| `docs/knowledge-base/README.md` | not_applicable | 当前知识库无针对 `music-ingestion` 的专项条目 |
