# governance-workflow-tooling Specification

## Purpose
TBD - created by archiving change study-projecttilesfst-governance-hardening. Update Purpose after archive.
## Requirements
### Requirement: 跨项目治理学习应用

本项目 MUST 支持 `/spec-study` 以两阶段方式学习外部 Harness / OpenSpec / Agent 治理工程，并在用户确认后才将候选学习内容应用到本项目治理资产。

#### Scenario: 学习对象只读

- **WHEN** `/spec-study` 学习本地或远端项目
- **THEN** 学习对象 MUST 全程只读
- **AND** 不得在学习对象路径内写入、安装依赖、格式化、迁移、修复测试、清理、提交、重置或修改 Git 状态

#### Scenario: 日志优先学习和漂移复核

- **GIVEN** 学习对象存在 `docs/spec-logs/CHANGELOG.md`
- **WHEN** `/spec-study` 执行学习阶段
- **THEN** 命令 MUST 先读取日志索引和相关单次 study/governance 日志作为入口地图
- **AND** MUST 回到学习对象真实治理资产横向复核日志描述是否仍然成立
- **AND** 若日志与真实资产存在漂移，MUST 标注漂移风险，并以当前真实资产、active Change、Sprint 四件套和正式规格作为最终事实依据

#### Scenario: 应用阶段项目化改写

- **WHEN** 用户确认应用学习内容
- **THEN** 应用内容 MUST 按 ProjectSoulKing 的 `app/`、`app/static/`、SQLite、MinIO、Mintlify `docs.json` 和 `.agents/skills/` 边界重写
- **AND** 不得原样复制 ProjectTilesFST 的业务专属规则、脚本或源码语境
- **AND** 长期文档 MUST 遵守事实唯一归属，入口文件只写摘要和链接，详细规则写入最匹配的归属文档

#### Scenario: 学习报告决策字段

- **WHEN** `/spec-study apply` 生成学习报告
- **THEN** 报告 MUST 记录已采纳原因、未采纳原因、替代方案或取舍、验证责任和后续触发条件
- **AND** 报告 MUST NOT 包含会话推理、临时草稿、review 对话、未脱敏本机路径、学习对象源码或不可解析引用

### Requirement: 治理上下文预算

本项目 MUST 通过规则和脚本约束 Agent 的读取范围、摘要复用、宽泛搜索和命令输出契约。

#### Scenario: 命令最终输出契约卫生

- **WHEN** 命令技能定义最终输出契约
- **THEN** 技能 MUST 要求最终回复输出真实结果
- **AND** 不得给出可被原样复制的尖括号占位模板、与当前命令无关的通用示例或 `MUST` / `SHOULD` 规范语气
- **AND** `scripts/validate-agent-context-budget.py` MUST 拦截最终输出占位模板、通用 BUG 示例、重复诱因和规范语气泄漏风险

### Requirement: 目录与公开材料边界

本项目 MUST 通过 `rules/directory-structure.md` 与 `scripts/validate-directory-structure.py` 约束 deploy、Mintlify、release、spec logs 和真实 env 文件。

#### Scenario: 真实 env 不阻断但不可提交

- **WHEN** 本地存在被 `.gitignore` 覆盖且未被 Git 跟踪的真实 env 文件
- **THEN** 目录结构、OpenSpec 归档和 Sprint 归档校验 MUST NOT 因存在本身阻断
- **AND** 如果真实 env 被 Git 跟踪、暂存，或内容进入 release、Mintlify、archive evidence、AI Usage、日志或回复，MUST 阻断

#### Scenario: Mintlify 投影边界

- **WHEN** 发布版本包含产品使用文档或公告投影
- **THEN** `releases/<version>/usage-docs/manifest.json` 或 `releases/<version>/release.json` MUST 保持事实源地位
- **AND** `mintlify/` 只能作为公开站点源目录和投影结果

### Requirement: Agent 治理命令必须提供可校验的流程门禁

Agent 治理命令 MUST 通过项目规则、技能文档和校验脚本约束命令顺序、Sprint Inclusion Gate、上下文预算、学习对象只读保护、Git 安全检查和最终输出契约。

#### Scenario: Sprint 选择与连续编号门禁

- **WHEN** `/sprint-propose` 选择或创建 Sprint
- **THEN** 命令 SHOULD 先运行 `python scripts/validate-sprint-selection.py [--sprint <sprint-id>]`
- **AND** 未指定 Sprint 时 MUST 按 active Sprint 数量选择、默认当前 Sprint 或阻断
- **AND** 新建 Sprint MUST 使用最大规范编号加一
- **AND** 已存在两个 active Sprint 时 MUST 阻断创建第三个 active Sprint

#### Scenario: Sprint 人读规划源一致性

- **WHEN** `/sprint-propose` 新建、追加或修正 Sprint 正式范围
- **THEN** 命令 MUST 以 `sprint.yaml` 作为机器事实源
- **AND** 必须通过 Workflow Sync 刷新 `sprint.md`、`release-note.md`、`acceptance-report.md`、Issue trace 和 Change trace
- **AND** `python scripts/validate-sprint-scope.py <sprint-id> [--item <id>]` MUST 校验 `sprint.md` `## 1. 目标` 编号列表、`## 2. Scope` 六列主表和派生 Scope 表均包含正式范围
- **AND** `## 2. Scope` 主表 MUST 保持 `类型 | 编号 | 标题 | 状态 | 估算 | 说明` 六列

#### Scenario: Sprint 归档 stale scan

- **WHEN** `/sprint-archive` 关闭 Sprint
- **THEN** archive readiness MUST 执行 Sprint close stale scan
- **AND** 四件套和 scoped REQ/BUG 子文档不得残留与真实生命周期冲突的待命令、待实现、待验收、active Change 路径或 legacy archive canonical 路径
- **AND** 10 个及以上 Change 的 Sprint MUST 优先检查 `change_batches` 摘要，再读取必要原始 Change 文档

#### Scenario: BUG review confirmed 根因门禁

- **WHEN** `/bug-review <BUG-full-id>` 走默认 approve 或显式 approve 路径
- **THEN** 命令 MUST 运行 `python scripts/validate-root-cause-evidence.py --bug <BUG-id> --require-confirmed`
- **AND** `unknown`、`hypothesis`、`probable`、缺少 `root-cause.md` 或缺少根因状态均 MUST 阻断 approve
- **AND** confirmed 根因缺少可定位证据链时 MUST 阻断 approve

#### Scenario: AI Usage 矩阵 unknown 语义

- **WHEN** Sprint Fact Sheet 输出 AI Usage 矩阵
- **THEN** 原始矩阵列状态 MUST 区分 `observed` 与 `unknown`
- **AND** 用户可见矩阵 MUST 将 `unknown` workflow 列渲染为 `-`
- **AND** `-` MUST 表示该 workflow 阶段未采集或未归因，不得等同于真实数字 `0`
- **AND** 只有 fresh gate、actual/present snapshot 和矩阵写入门禁均通过时，才可输出真实成本矩阵

### Requirement: REQ 和 BUG 评审命令默认通过

本项目 MUST 将无显式结果 flag 的 `/req-review <REQ-full-id>` 与 `/bug-review <BUG-full-id>` 解释为 `approve`，以降低常规评审通过路径的重复输入成本。

#### Scenario: 需求评审无 flag 默认批准

- **WHEN** 用户运行 `/req-review <REQ-full-id>` 且未提供 `--reject` 或 `--defer`
- **THEN** 命令 MUST 按 `approve` 结果执行
- **AND** MUST 生成或更新 `review.md`
- **AND** MUST 更新 `trace.md` 与 `requirement.md` 状态为 `approved`
- **AND** MUST 按批准路径执行目录迁移、Workflow Sync 与 AI Usage hook

#### Scenario: 缺陷评审无 flag 默认批准

- **WHEN** 用户运行 `/bug-review <BUG-full-id>` 且未提供 `--reject`、`--defer` 或 `--wont-fix`
- **THEN** 命令 MUST 按 `approve` 结果执行
- **AND** MUST 生成或更新 `review.md`
- **AND** MUST 更新相关 BUG 状态为 `approved`
- **AND** MUST 按批准路径执行目录迁移、Workflow Sync 与 AI Usage hook

#### Scenario: 非通过结论必须显式声明

- **WHEN** 用户希望评审结论为拒绝、延后或不修复
- **THEN** 命令 MUST 要求用户显式提供对应 flag
- **AND** `/req-review` MUST 仅接受 `--reject` 或 `--defer` 作为非通过结果
- **AND** `/bug-review` MUST 接受 `--reject`、`--defer` 或 `--wont-fix` 作为非通过结果

#### Scenario: 下一步提示省略常规 approve flag

- **WHEN** 命令、规则或文档推荐常规 REQ/BUG 评审通过路径
- **THEN** 下一步命令 SHOULD 使用 `/req-review <REQ-full-id>` 或 `/bug-review <BUG-full-id>`
- **AND** 不应在常规通过示例中继续要求 `--approve`

### Requirement: 版本升级路径治理

本项目 MUST 支持以治理脚本和 Agent 技能记录 `from_version -> to_version` 的部署升级路径、支持级别、备份、回滚和 smoke 证据。

#### Scenario: 生成升级计划

- **WHEN** 用户运行 `/upgrade-plan --from <fresh|version> --to <version>`
- **THEN** 命令 MUST 生成或更新 `releases/<to-version>/upgrade-plans/<from>-to-<to>.json`
- **AND** 计划 MUST 记录目标 release、目标 image manifest、`SOULKING_IMAGE_TAG`、SQLite 备份要求、env diff、MinIO 对象存储影响、升级步骤、回滚步骤、blockers、warnings 和 evidence
- **AND** 命令 MUST NOT 自动执行生产升级、修改真实 env、恢复数据库或写入对象存储

#### Scenario: 校验升级计划

- **WHEN** 用户运行 `/upgrade-validate --plan <path>`
- **THEN** 命令 MUST 校验升级计划必填字段、支持级别、回滚块和公开安全边界
- **AND** 输出 MUST 只包含摘要、blocker/warning 和修复建议
- **AND** 不得输出真实 `.env` 值、密钥、数据库文件路径、Authorization header、Cookie 或本机绝对路径

### Requirement: 证据化根因分析

本项目 MUST 在问题排查、BUG 完善、BUG 来源实现和验收返修中区分根因证据强度，避免把推测包装成确认结论。

#### Scenario: 根因状态与证据链

- **WHEN** `root-cause.md` 或相关治理记录声明根因为 `confirmed`
- **THEN** 文档 MUST 记录可定位的脱敏证据链
- **AND** 证据链 SHOULD 包含复现、日志、测试、截图、配置差异、数据样本或代码定位等摘要

#### Scenario: 证据不足时保留不确定性

- **WHEN** 根因状态为 `unknown`、`hypothesis` 或 `probable`
- **THEN** 文档 MUST 说明仍需补充的证据或验证步骤
- **AND** 命令不得将该状态表述为已确认根因

### Requirement: 音乐媒体资产验收模板

本项目 MUST 为音频、歌词、封面、头像和对象存储相关变更提供统一的媒体资产验收记录口径。

#### Scenario: 媒体资产五维验收

- **WHEN** REQ、BUG、OpenSpec Change、Sprint 或 release 触达音乐媒体链路
- **THEN** 验收记录 SHOULD 按 `key`、`object`、`URL / playback`、`metadata`、`UI render` 五个维度记录结论
- **AND** 任一维度为 `fail` 或 `blocked` 时，整体结论不得写为 `pass`
- **AND** 记录不得包含真实密钥、访问令牌、完整私有对象 URL、未脱敏日志或本机绝对路径

### Requirement: 数据采集治理学习应用

Agent 治理命令 SHALL 能通过 `/spec-study apply` 将外部项目的数据采集治理经验项目化应用到 SoulKing 的规则、技能、标准文档和校验脚本中。

#### Scenario: 数据采集治理项目化改写

- **GIVEN** 用户确认应用 TilesFST 数据采集学习项
- **WHEN** `/spec-study apply TilesFST --items D1,D2,D3,D4` 修改治理资产
- **THEN** 变更 SHALL 通过 active OpenSpec Change 和 Sprint scope 承载
- **AND** 学习对象 SHALL 保持只读
- **AND** 本项目 SHALL 生成单份 `docs/spec-logs/YYYYMMDDhhmmss-study-tilesfst-data-collection.md` 学习报告
- **AND** 应用内容 SHALL 使用 SoulKing 音乐资产、SQLite、MinIO、前台 Web、后台管理端和 `.agents/skills/` 语境重写

### Requirement: Sprint 容量门禁

本项目 SHALL 在 Sprint 提议和正式范围追加阶段计算容量占用率，并根据容量区间决定是否通过、风险通过或硬阻断。

#### Scenario: 新建 Sprint 使用项目默认容量基线

- **WHEN** `/sprint-propose` 创建新的 Sprint
- **AND** `project.yaml` 配置了 `ai.sprint_capacity.capacity_person_days`
- **THEN** 系统 MUST 默认使用该值作为新 Sprint 的 `capacity_person_days`
- **AND** `sprint.yaml.capacity_gate.capacity_person_days` MUST 与该容量基线保持一致

#### Scenario: 容量不超过计划基线时正常通过

- **WHEN** `/sprint-propose` 或范围追加评估候选范围
- **AND** `estimated_person_days <= capacity_person_days`
- **THEN** 系统 MUST 按既有 Review Gate、Readiness Gate、Sprint Selection Gate 和 Scope Gate 继续
- **AND** `capacity_gate.result` MUST 记录为 `pass`

#### Scenario: 容量超过 100% 且不超过 120% 时风险通过

- **WHEN** `/sprint-propose` 或范围追加评估候选范围
- **AND** `capacity_person_days < estimated_person_days <= capacity_person_days * 1.2`
- **THEN** 系统 MAY 继续生成或更新 Sprint 正式范围
- **AND** Sprint 文档 MUST 记录容量风险、fix 缓冲影响和延后项建议
- **AND** `capacity_gate.result` MUST 记录为 `pass_with_risk`

#### Scenario: 容量超过 120% 时硬阻断

- **WHEN** `/sprint-propose` 或范围追加评估候选范围
- **AND** `estimated_person_days > capacity_person_days * 1.2`
- **THEN** 系统 MUST 阻断正式规划写入
- **AND** 系统 MUST NOT 生成 `iterations/change/<sprint>/` 四件套
- **AND** 系统 MUST NOT 更新 REQ、BUG 或 Change trace 的 Sprint 关联
- **AND** 系统 MUST 提示拆分 Sprint、移出低优先级项或替换范围后重新评估
- **AND** `capacity_gate.result` MUST 记录为 `blocked`，如果候选数据已经进入临时评估对象

#### Scenario: 容量字段缺失时不得默认通过

- **WHEN** `/sprint-propose` 或范围追加无法获得 `capacity_person_days` 或 `estimated_person_days`
- **THEN** 系统 MUST 停止容量门禁
- **AND** 系统 MUST 提示先补齐容量或估算输入

#### Scenario: sprint.yaml 保存容量门禁字段

- **WHEN** Sprint 正式范围被创建、追加或修正
- **THEN** `sprint.yaml` MUST 记录 `capacity_person_days`、`estimated_person_days`、`capacity_usage`、`fix_buffer_person_days`、`fix_buffer_ratio` 和 `capacity_gate`
- **AND** `capacity_gate` MUST 至少包含 `capacity_person_days`、`estimated_person_days`、`capacity_usage`、`result` 和 `note`

