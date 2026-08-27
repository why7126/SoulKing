---
purpose: OpenSpec 项目说明
content: ProjectSoulKing 的技术栈、领域背景、开发约束和变更流程入口
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# ProjectSoulKing OpenSpec 项目说明

ProjectSoulKing 是私有化个人音乐资产管理系统。当前实现基于 FastAPI、SQLite、MinIO 和静态 HTML/CSS/JavaScript。

## 技术栈

- 后端：Python 3.12、FastAPI、Pydantic、SQLAlchemy。
- 前端：`app/static/` 原生 HTML/CSS/JavaScript。
- 数据库：SQLite，运行时数据位于 `data/`。
- 对象存储：并列 `ProjectMinio`，当前单桶 `soulking`。
- 部署：Docker Compose 启动 app，MinIO 由外部 compose 提供。

## 领域约束

- 音频导入以内容指纹和歌曲语义共同去重。
- 对象键可随歌曲、艺人和文件名变化而迁移。
- 用户认证和管理员保护是已启用能力。
- 前台和后台 UI 必须遵守 `ui-design.md` 的双皮肤 CSS 架构。

## OpenSpec 约束

- 新能力、接口、数据结构、权限、存储或部署变化必须创建 `openspec/changes/<change-id>/`。
- 已生效能力在 `openspec/specs/`，除归档合并外不得直接改。
- 归档时必须更新对应 specs、记录验证结果并运行工作流同步。
