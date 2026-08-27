---
req_id: REQ-0015-admin-bulk-export
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/admin-bulk-export/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：管理端音频批量导出。

# 原始描述
基于项目内已生效规格 `openspec/specs/admin-bulk-export/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/admin-bulk-export/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「管理端批量导出音频」能力：通过专用接口按所选曲目集合与所选音频格式，收集各曲目下实际存在的音频文件，并以 **单文件流式下载** 或 **ZIP 压缩包** 返回。本规范仅描述 **`POST` 批量下载接口** 的服务端行为；管理界面中单首曲目、多格式时使用浏览器跳转至曲目下载路径的行为不在此接口条目中展开，但与批量接口共用相同的打包与命名辅助逻辑。本规范 **不包含** 元数据表格导出、非音频文件导出。
