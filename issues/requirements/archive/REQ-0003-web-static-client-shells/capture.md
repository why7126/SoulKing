---
req_id: REQ-0003-web-static-client-shells
status: archived
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
recorded_at: 2026-07-15 00:00:00
recorded_by: codex
source: openspec/specs/web-static-client-shells/spec.md
priority_hint: P1
parent_requirement:
---

# 一句话
回填并归档当前已实现能力：Web 静态前后台客户端壳。

# 原始描述
基于项目内已生效规格 `openspec/specs/web-static-client-shells/spec.md`、产品文档与代码现状，整理该能力对应的需求资产。

# 待澄清
- [x] 已以 `openspec/specs/web-static-client-shells/spec.md` 作为当前事实源。
- [x] 本次为历史已实现能力回填，不进入新的实现 Sprint。

# 探索结论
定义「Web 静态客户端壳」能力：服务端将静态资源目录以固定 URL 前缀对外提供；通过两条入口路径分别交付 **前台壳** 与 **后台壳** 的 HTML 文档；文档内挂载样式表与 **单一 ES 模块脚本入口**，由脚本调用后端接口并驱动界面（前台默认将站内路径拼为同源 URL）。本规范仅描述壳层交付与跨页导航；具体业务（曲库、歌单、扫描等）由其它能力规范覆盖。仓库中另有未接入任一脚本页的静态脚本文件，见 Known Gaps。
