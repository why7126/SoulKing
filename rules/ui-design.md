---
purpose: UI 设计规范
content: ProjectSoulKing 前台、后台、登录页视觉与交互执行规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-10 23:20:00
---

# UI 设计规范

UI 事实源为 `ui-design.md` 和 `app/static/` 现有实现。

- 前台使用 `studio.css` 的 `--sk-*` 令牌和 `btn-studio-*` 组件。
- 后台使用 `admin-studio.css` 的 `--adm-*` 令牌和 `btn-adm-*` 组件。
- 登录页使用 `login.css`，保持与 Studio 深色紫色体系一致。
- 新增 UI 不得破坏前台侧栏、后台表格、编辑抽屉、底部播放条和用户菜单的布局稳定性。
- 头像 presigned URL 不得在前端追加未签名查询参数。
- 带 `prototype/`、`prototype_refs`、`AC-PROTOTYPE-*` 或 UI Skeleton 的 Change 必须遵守 `docs/standards/prototype-ui-acceptance.md`。
- `/req-opsx` 应在 Change `design.md` 中写入 UI Contract；`/opsx-apply` 完成前应记录 1440px 截图、关键交互证据和必要 computed style。
