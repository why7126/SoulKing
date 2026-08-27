---
purpose: 规范工程日志
content: 为规范工程变更历史新增跨项目落地提示词列
created_at: 2026-08-08 21:02:26
updated_at: 2026-08-08 21:02:26
---

# 为规范工程变更历史新增跨项目落地提示词列

## 迭代目标

在 `docs/spec-logs/CHANGELOG.md` 的变更历史列表中新增 `其他项目落地提示词` 列，用于记录其他项目希望复用同类规范、脚本、命令或治理流程时可直接使用的 Prompt。

## OpenSpec Change 豁免说明

本次仅调整治理日志索引字段和记录内容，不新增命令、不改变脚本校验行为、不改变业务能力、接口契约、数据结构、部署拓扑或权限边界，因此按 `/spec-opt` 非行为性文档补强规则豁免 active OpenSpec Change。

## 变更摘要

- 为 `docs/spec-logs/CHANGELOG.md` 变更历史表新增 `其他项目落地提示词` 列。
- 为既有两条历史记录补充可复用 Prompt。
- 追加本次治理变更记录，形成后续跨项目复用提示词的记录样例。

## 影响范围

- `docs`：更新规范工程变更历史索引并新增本次治理日志。
- `rules`：未修改。
- `scripts`：未修改。
- `.agents/skills`：未修改。
- `AGENTS`：未修改。
- `OpenSpec`：未创建或修改 active Change。

## 更新文件

- `docs/spec-logs/CHANGELOG.md`
- `docs/spec-logs/20260808210226-governance-spec-logs-adoption-prompt.md`

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

后续每条变更历史都应补充可落地提示词；若提示词涉及参考项目，应使用 `<参考项目名>`、`<目标项目名>` 等占位符，避免写入本机绝对路径或敏感上下文。
