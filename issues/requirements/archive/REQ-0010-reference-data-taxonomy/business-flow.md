---
requirement_id: REQ-0010-reference-data-taxonomy
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
source: requirement.md
---

# 业务流程

```text
用户/客户端
  -> 访问 ProjectSoulKing Web 壳或 REST API
  -> 触发 参考数据与分类体系管理 能力
  -> 服务端按 `reference-data-taxonomy` 规格校验权限、参数与业务状态
  -> 读写 SQLite / MinIO / 静态资源（按能力需要）
  -> 返回业务结果、错误或下载/播放响应
```

## 与父需求差异
- 本需求为历史实现能力回填，无父需求。

## 关键边界
- 权限、数据一致性、对象存储、UI 展示和错误形态均以 `openspec/specs/reference-data-taxonomy/spec.md` 为准。
- 后续改变边界时必须新建 OpenSpec Change。
