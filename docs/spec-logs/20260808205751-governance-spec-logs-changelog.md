---
purpose: 规范工程日志
content: 新增规范工程变更历史索引
created_at: 2026-08-08 20:57:51
updated_at: 2026-08-08 20:57:51
---

# 新增规范工程变更历史索引

## 迭代目标

在 `docs/spec-logs/` 下新增规范工程变更历史文档，用于持续记录每一次规范、脚本、命令和治理流程更新日志，并让后续 `/spec-study`、`/spec-opt` 产物可以被统一检索。

## OpenSpec Change 豁免说明

本次仅新增治理日志索引和文档入口说明，不新增命令、不改变脚本校验行为、不改变业务能力、接口契约、数据结构、部署拓扑或权限边界，因此按 `/spec-opt` 非行为性文档补强规则豁免 active OpenSpec Change。

## 变更摘要

- 新增 `docs/spec-logs/CHANGELOG.md`，作为规范工程累计变更历史索引。
- 在文档索引中补充 `CHANGELOG.md` 入口。
- 在目录结构规范中明确 `docs/spec-logs/CHANGELOG.md` 的职责和记录要求。
- 保持单次详细日志继续使用 `YYYYMMDDhhmmss-study-xxx.md` 与 `YYYYMMDDhhmmss-governance-xxx.md`。

## 影响范围

- `docs`：新增规范工程变更历史索引和本次治理日志。
- `rules`：补充 `docs/spec-logs/` 目录职责说明。
- `scripts`：未修改。
- `.agents/skills`：未修改。
- `AGENTS`：未修改。
- `OpenSpec`：未创建或修改 active Change。

## 更新文件

- `docs/spec-logs/CHANGELOG.md`
- `docs/spec-logs/20260808205751-governance-spec-logs-changelog.md`
- `docs/README.md`
- `rules/directory-structure.md`

## 验证结果

- `python scripts/validate-generated-docs.py --strict`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。

## API / DB / 前台 Web / 后台管理端 / 桌面封装 / 对象存储 / Docker 影响

- API：无影响。
- DB：无影响。
- 前台 Web：无影响。
- 后台管理端：无影响。
- 桌面封装：无影响。
- 对象存储：无影响。
- Docker：无影响。

## 后续建议

后续每次新增或调整规范、脚本、命令、目录边界、发布治理、部署治理或 Mintlify 治理时，应同步追加 `docs/spec-logs/CHANGELOG.md`，并链接对应时间戳详细日志。
