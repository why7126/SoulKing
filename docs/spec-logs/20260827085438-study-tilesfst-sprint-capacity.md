---
purpose: 跨项目学习报告
content: ProjectTilesFST Sprint 容量配置和超出策略学习应用
created_at: 2026-08-27 08:54:38
updated_at: 2026-08-27 08:54:38
---

# ProjectTilesFST Sprint 容量治理学习应用

## 1. 学习对象与模式

- 学习对象：`<local-project>/ProjectTilesFST`
- 学习模式：`auto`
- 执行时间：2026-08-27 08:54:38
- 应用 Change：`tighten-soulking-sprint-capacity-governance`
- 承载 Sprint：`sprint-002`

## 2. 学习到的治理能力

- Sprint 容量使用 `capacity_usage = estimated_person_days / capacity_person_days` 统一计算。
- 容量不超过 100% 时正常通过；100% 到 120% 时风险通过并记录风险；超过 120% 时硬阻断正式规划写入。
- Sprint 选择门禁与容量硬阻断联动：已有 active Sprint 时，只有当前 Sprint 容量硬阻断或用户明确拆分范围，才允许创建下一个连续 Sprint。
- `sprint.yaml` 应记录 `capacity_person_days`、`capacity_usage`、`fix_buffer_person_days`、`fix_buffer_ratio` 和 `capacity_gate`，避免人读文档与机器事实源漂移。
- 容量策略需要规则、技能、OpenSpec 规格和聚焦测试共同约束，不能只停留在 Sprint 文档说明。

## 3. 已采纳内容

| 项 | 内容 | 采纳原因 |
|---|---|---|
| A1 | 在 `governance-workflow-tooling` 增加 Sprint 容量门禁 delta spec | SoulKing 已有治理工作流能力，适合承载 Sprint 规划门禁 |
| A2 | 更新 Sprint 生命周期规则三段式容量策略 | 当前规则只有超过 120% 引导，缺少完整门禁 |
| A3 | 更新 `/sprint-propose` 容量门禁和 Sprint 字段模板 | 命令执行阶段需要在写入前阻断超载范围 |
| A4 | 新增容量门禁聚焦测试 | 防止规则、技能和 spec 后续漂移 |
| A5 | 更新 `add-sprint-scope-item.py` capacity gate 刷新逻辑 | 追加范围时需要同步刷新机器事实源中的 gate 结果 |
| A6 | 将 SoulKing 项目默认 Sprint 容量基线调整为 30 人天 | 用户确认采用 30 人天作为后续新建 Sprint 默认容量 |

## 4. 未采纳内容

| 内容 | 未采纳原因 | 替代方案 |
|---|---|---|
| 反向修改 `sprint-001` 作为本次学习的一部分 | `sprint-001` 是既有超载 Sprint，本次应用应由新的治理 Change 和 `sprint-002` 承载 | 后续如需修正 `sprint-001`，单独走 Sprint 修正或归档前同步流程 |

## 5. 更新文件

| 文件 | 修改原因 |
|---|---|
| `openspec/changes/tighten-soulking-sprint-capacity-governance/` | 承载本次治理应用的 OpenSpec Change |
| `iterations/change/sprint-002/` | 承载本次 Change 的 Sprint 四件套 |
| `rules/iterations-lifecycle.md` | 写入 Sprint 容量门禁事实源 |
| `.agents/skills/sprint-propose/SKILL.md` | 写入命令执行门禁和 `sprint.yaml` 字段模板 |
| `scripts/add-sprint-scope-item.py` | 追加范围时同步刷新 `capacity_gate` 结果和说明 |
| `tests/test_sprint_propose_capacity_gate.py` | 覆盖规则、技能、spec 与脚本刷新逻辑 |
| `docs/spec-logs/20260827085438-study-tilesfst-sprint-capacity.md` | 记录本次跨项目学习应用 |
| `project.yaml` | 记录 SoulKing 新建 Sprint 默认容量基线 30 人天 |
| `iterations/change/sprint-002/` | 同步当前承载 Sprint 的容量字段和容量说明 |

## 6. 影响范围

- API：无影响。
- 数据库：无影响。
- 前台 Web：无影响。
- 后台管理端：无影响。
- 桌面封装：无影响。
- 对象存储：无影响。
- Docker Compose：无影响。
- 测试：新增治理脚本聚焦测试。

## 7. 验证责任和后续触发条件

- 本次交付前运行容量门禁聚焦测试、上下文预算、OpenSpec 语言、目录结构、OpenSpec validate、Sprint scope 和文档卫生校验。
- 后续每次 `/sprint-propose` 或已有 Sprint 追加范围时，容量字段和 gate 结果应以 `sprint.yaml` 为机器事实源。
- 若 SoulKing 后续团队规模变化，应先调整 `project.yaml` 的默认容量基线；已存在 Sprint 是否同步调整需按 Sprint 修正流程单独确认。

## 8. 只读保护

学习对象只执行了读取、搜索和 Git 状态查看类命令。学习对象工作区存在既有未提交改动，但本流程未对学习对象执行写入、安装、格式化、迁移、测试修复、提交、重置或清理命令。

## 9. 后续建议

- 在 `sprint-001` 归档前复核容量字段和 `sprint.md` 工作量段，避免历史文档继续显示错误容量占用。
- 后续可把容量门禁前置为独立脚本，供 `/sprint-propose --dry-run` 和 CI 复用。
