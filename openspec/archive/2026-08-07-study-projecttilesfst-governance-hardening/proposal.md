---
created_at: 2026-08-07 12:30:00
updated_at: 2026-08-07 12:30:00
---

# 跨项目治理学习加固

## 背景

ProjectSoulKing 已引入 `/spec-study`，用户确认将 ProjectTilesFST 中适合本项目的 `agent-context-budget`、`directory-structure`、`deploy-mintlify-release` 治理经验应用到本项目。

当前本项目已有基础规则和校验脚本，但入口文档、目录结构、部署/Mintlify/release 边界、上下文预算规则仍可更明确，避免后续跨项目学习或发布治理时出现重复读大文件、目录边界漂移、真实 env 泄露、Mintlify 与 release 事实源混用等问题。

## 变更目标

- 加强 `AGENTS.md` 的命令输出契约、完成检查清单和目录边界摘要。
- 加强 `rules/agent-context-budget.md` 的已读摘要复用、默认搜索排除和 `spec-study/spec-opt` 约束。
- 加强 `rules/directory-structure.md` 对 `deploy/`、`mintlify/`、`docs/spec-logs/` 和真实 env 的边界说明。
- 加强 release / usage docs / Mintlify 规则，使 release 快照继续作为事实源，Mintlify 仅作为公开站点投影。
- 加强目录校验和 Mintlify 校验脚本，确保规则可真实运行。

## 非目标

- 不修改 `app/`、`app/static/`、`packaging/` 业务运行时代码。
- 不同步 ProjectTilesFST 的瓷砖、小程序、MySQL、Orval、订单、客户、SKU、证书图片等业务专属规则或脚本。
- 不修改 ProjectTilesFST 中任何文件。

## 风险

- 规则加强后，后续治理命令可能更早暴露目录或发布材料不规范的问题。
- 若过度照搬 TilesFST 的 `src/` / MySQL / 小程序语境，会与 SoulKing 当前 FastAPI + SQLite + 静态 Web 壳架构冲突；本变更必须项目化改写。
