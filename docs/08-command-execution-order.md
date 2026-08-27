---
purpose: 命令执行顺序速查
content: ProjectSoulKing REQ/BUG、Sprint、OpenSpec、发布、镜像与产品手册命令顺序和串行门禁
created_at: 2026-08-10 23:20:00
updated_at: 2026-08-27 01:30:00
---

# 命令执行顺序速查

本文约束 AI 在 ProjectSoulKing 中推荐和执行工作流命令的顺序。原则是先记录事实源，再评审，再纳入 Sprint，再创建 Change，再实现与归档；发布、镜像和产品手册位于交付闭环之后。

治理命令还应遵守“事实源先行、最小相关验证、状态同步收尾”的顺序。选择验证前先看本次 diff scope 和触达面；已通过且未被后续改动影响的检查，不需要因为最终汇报而机械重复。OpenSpec、Sprint、Workflow Sync、AI Usage 等项目强制门禁仍必须按命令技能执行。

## 标准链路

```text
/req-capture 或 /bug-capture
→ /req-generate 或 /bug-generate
→ /req-complete 或 /bug-complete
→ /req-review 或 /bug-review
→ /sprint-propose
→ /req-opsx 或 /bug-opsx
→ /opsx-apply
→ /opsx-modify（可选）
→ /opsx-archive
→ /sprint-archive
→ /sprint-exps
→ /release-propose
→ /release-prepare
→ /usage-docs-generate 或 /usage-docs-update 或 /usage-docs-validate
→ /image-prepare
→ /image-build
→ /release-publish
```

## REQ / BUG 到 OpenSpec

- 未评审的 REQ/BUG 不得进入 Sprint、不得转 OpenSpec、不得执行开发。
- 已评审 REQ/BUG MUST 先通过 `/sprint-propose` 纳入 Sprint，并由 Workflow Sync 同步为 `in_sprint`，再通过 `/req-opsx` 或 `/bug-opsx` 创建 Change。
- `/req-review` 与 `/bug-review` 无 flag 时默认通过；下一步 MUST 分别是 `/sprint-propose --req <REQ-full-id>` 与 `/sprint-propose --bug <BUG-full-id>`。
- `/req-opsx` 和 `/bug-opsx` 遇到 `status: approved` 但尚未 `in_sprint` 时 MUST 停止，并提示先运行对应 `/sprint-propose`。
- `/req-opsx` / `/bug-opsx` 完成后 MUST 运行 Workflow Sync，把新 Change 回填到同一个 Sprint 的 `changes[]` 与 `scope_estimates[].change`。

## Apply / Modify / Archive

- `/opsx-apply` 前 MUST 通过 `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run` 确认目标 Change 位于 Sprint scope。
- `/opsx-modify` 只用于 `/opsx-apply` 之后、`/opsx-archive` 之前的验收返修；超出原 Change 范围时应创建新 REQ/BUG 或新 Change。
- `/opsx-archive` 只能归档已完成 tasks 且 artifact 完整的 Change。
- 归档步骤必须严格串行：归档脚本或 OpenSpec archive → 目录校验 → archive evidence → Workflow Sync → Issue promote → AI Usage。

## Sprint

- `sprint.yaml` 是 Sprint scope 的机器事实源；不得只手工编辑 `sprint.md`。
- `/sprint-propose` 选择或创建 Sprint 前 SHOULD 运行 `python scripts/validate-sprint-selection.py [--sprint <sprint-id>]`；多个 active Sprint 时必须显式指定，创建新 Sprint 必须使用最大规范编号加一。
- 已存在 Sprint 追加范围时，先运行 `scripts/add-sprint-scope-item.py` 更新 `sprint.yaml`，再运行 Workflow Sync 和 `validate-sprint-scope.py`；校验必须覆盖 `sprint.md` 的 `## 1. 目标` 编号列表、`## 2. Scope` 六列主表和派生 Scope 表。
- 多个范围项写入同一个 Sprint 时必须串行运行，不得并行写同一个 `sprint.yaml`。
- 关闭 Sprint 前必须通过 archive readiness 内置 stale scan；若四件套或 scoped Issue 子文档仍包含已归档 Change 的 active 路径、中间态文案或旧 `openspec/changes/archive/` canonical 引用，先修复事实同步或人工说明后再归档。

## 治理脚本门禁矩阵

| 触达范围 | 最小相关校验 |
|---|---|
| `.agents/skills/`、`rules/agent-context-budget.md` | `python scripts/validate-agent-context-budget.py` |
| Sprint 选择与连续编号 | `python scripts/validate-sprint-selection.py [--sprint <sprint-id>]` |
| OpenSpec Change 文档或 delta spec | `python scripts/validate-openspec-language.py`、`openspec validate <change-id>` |
| 目录边界、docs、issues、iterations、releases、mintlify、deploy | `python scripts/validate-directory-structure.py` |
| 长期文档、规则、技能说明、知识库 | `python scripts/validate-doc-prose-hygiene.py <focused-paths>` |
| BUG 根因、返修根因或问题排查证据 | `python scripts/validate-root-cause-evidence.py --bug <BUG-id>` 或 `--change <change-id>` |
| 产品数据采集、请求日志、行为事件、Task Trace、媒体链路或对象存储观测 | `python scripts/validate-product-data-observability-standard.py`、`python scripts/validate-product-data-observability-gates.py --change <change-id>` |
| 版本升级计划 | `python scripts/validate-release-upgrade.py validate-plan --plan <plan-path>` |
| Sprint scope | `python scripts/validate-sprint-scope.py <sprint-id> --item <change-id|REQ|BUG>` |
| API / OpenAPI | API 治理校验和相关测试 |
| DB schema | DB 文档、迁移兼容说明和相关测试 |
| UI / prototype | 相关静态检查、浏览器验证或截图证据；prototype 场景遵守 `docs/standards/prototype-ui-acceptance.md` |
| 发布 / usage docs / Mintlify | release、usage-docs、Mintlify 和部署 config 校验 |
| 安全 / env / 本地数据 | `python scripts/git-check.py` 或聚焦安全脚本 |

## 下一步参数规则

- REQ 链路的所有 `/req-*` 和后续 `/opsx-*` 下一步命令 MUST 使用完整 `REQ-xxxx-slug`。
- BUG 链路的所有 `/bug-*` 和后续 `/opsx-*` 下一步命令 MUST 使用完整 `BUG-xxxx-slug`。
- 无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>` 作为 `/opsx-*` 参数。
- 「下一步」只放可直接执行的命令；「待用户决策/处理」只放缺失输入、范围选择、证据补充、验收或发布确认、阻塞项。

## 串行写入边界

以下步骤写入同一事实源，MUST 严格串行执行：

- 多次运行 `scripts/add-sprint-scope-item.py` 写同一个 `sprint.yaml`。
- Workflow Sync 写 Sprint 派生表、Issue trace、registry 或验收回填。
- Issue 物理阶段迁移脚本。
- AI Usage hook 刷新同一 Sprint 或 release snapshot。
