---
requirement_id: REQ-0015-admin-bulk-export
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
source: requirement.md
---

# 用户故事

- US-001：批量下载请求体
- US-002：请求参数去重与顺序
- US-003：按曲目与格式收集音频文件
- US-004：无可下载文件时的错误
- US-005：单文件响应
- US-006：多文件 ZIP 响应
- US-007：ZIP 包内文件名分配
- US-008：ZIP 打包时的单项失败容错

## 验收要点
- 用户能够按 `admin-bulk-export` 已生效规格描述完成对应业务目标。
- 异常、空状态、权限或边界行为以规格中的 Scenario 为准。
