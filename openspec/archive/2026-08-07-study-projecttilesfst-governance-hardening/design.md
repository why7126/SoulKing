---
created_at: 2026-08-07 12:30:00
updated_at: 2026-08-07 12:30:00
---

# 设计

## 方案

采用“规则 + 脚本 + 学习报告”三层同步：

- 规则层：更新 `AGENTS.md`、`rules/agent-context-budget.md`、`rules/directory-structure.md`、`rules/release.md`、`docs/02-deployment.md`、`deploy/README.md`。
- 脚本层：更新 `scripts/validate-directory-structure.py` 和 `scripts/validate-mintlify-site.py`，让 deploy / Mintlify / 真实 env / spec logs 边界可校验。
- 报告层：更新同一份 `docs/spec-logs/*-study-projecttilesfst-spec-governance.md`，记录本次应用范围、未采纳内容、验证结果和学习对象只读保护。

## 项目化差异

ProjectTilesFST 的 `src/`、React、Orval、小程序、MySQL 和腾讯云 COS 语境不适合原样迁移。ProjectSoulKing 保持：

- 业务代码边界为 `app/`、`app/static/`、`packaging/`。
- 数据库事实源为 SQLite。
- 对象存储为 MinIO 单桶前缀策略。
- Mintlify 使用 `docs.json`，不是 `mint.json`。
- `/miniapp-*` 仅兼容保留，`project.yaml` 中 `wechat_miniapp.enabled=false` 时阻断执行。

## 校验策略

完成后运行：

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-directory-structure.py`
- `python scripts/validate-generated-docs.py --strict`
- `bash scripts/validate-openspec.sh`
- `python scripts/validate-mintlify-site.py`
- `python scripts/validate-release.py`

若脚本发现规则与现实目录不一致，优先修正规则或项目化校验，不放宽真实 env、构建产物、敏感信息边界。
