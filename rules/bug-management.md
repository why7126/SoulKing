---
purpose: BUG 管理
content: BUG 捕获、分析、修复准入、回归验证和事故复盘规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 00:00:00
---

# BUG 管理

- BUG 先进入 `issues/bugs/plan/`，记录复现步骤、期望、实际、影响范围和证据。
- `/bug-complete` 应补齐根因状态、证据链、修复策略、回归范围和风险；`root-cause.md` MUST 遵守 `rules/root-cause-evidence.md`。
- `/bug-review <BUG-full-id>` 无 flag 时默认通过；通过后必须先 `/sprint-propose --bug <BUG-full-id>` 纳入 Sprint，再 `/bug-opsx <BUG-full-id>`。
- `/bug-review` 默认 approve 或显式 approve 前，目标 BUG 的 `root-cause.md` MUST 满足 `root_cause_status: confirmed` 且证据链可定位；否则先补证或选择非通过评审结果。
- BUG 链路的下一步命令必须保留完整 `BUG-xxxx-slug`，包括后续 `/opsx-apply <BUG-full-id>`、`/opsx-modify <BUG-full-id>`、`/opsx-archive <BUG-full-id>`。
- `issues/bugs/CHANGELOG.md` 应维护每个 BUG 一行的当前态看板索引，但机器事实源仍是 `_registry.yaml`、单条 `trace.md`、Sprint 四件套和 OpenSpec Change。
- 修复后必须记录验证结果；涉及历史数据或对象存储时补充迁移验证。
- 系统性、隐蔽且复现成本高的 BUG 修复后 SHOULD 在 `docs/knowledge-base/incidents/` 生成事故复盘，记录现象、根因、遗漏的防线、补上的规则/测试/脚本和后续预防动作。
- 复盘不是普通 BUG 详情副本；只有当缺陷暴露测试、流程、规范或工具缺口时才需要生成，且应链接原 BUG、Change 和验证证据。
