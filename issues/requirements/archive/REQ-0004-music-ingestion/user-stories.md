---
requirement_id: REQ-0004-music-ingestion
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
source: requirement.md
---

# 用户故事

- US-001：目录扫描入口与路径校验
- US-002：上传文件入库入口
- US-003：音频格式白名单
- US-004：按内容去重
- US-005：单文件入库管线
- US-006：入库时歌曲标题与文件名
- US-007：主艺人关联范围
- US-008：目录扫描的任务记录与统计
- US-009：进程内进度与重置
- US-010：目录扫描的同步执行
- US-011：目录扫描时关联侧车 LRC 文件

## 验收要点
- 用户能够按 `music-ingestion` 已生效规格描述完成对应业务目标。
- 异常、空状态、权限或边界行为以规格中的 Scenario 为准。
