## MODIFIED Requirements

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

#### Scenario: 文档表达卫生校验

- **WHEN** 治理命令修改长期文档、规则、技能说明或知识库
- **THEN** 命令 SHOULD 运行 `python scripts/validate-doc-prose-hygiene.py <focused-paths>`
- **AND** 脚本 MUST 以 warning 级启发式结果提示会话推理、临时草稿、review 对话、历史叙事和不可解析路径风险
- **AND** 脚本 MUST NOT 自动删除或改写文档内容

#### Scenario: 最小相关验证矩阵

- **WHEN** 治理命令选择本地验证范围
- **THEN** 命令 SHOULD 根据本次 diff scope 和触达面选择最小相关校验
- **AND** 已通过且未被后续改动影响的检查不需要因为最终汇报而机械重复
- **AND** OpenSpec、Sprint、Workflow Sync 和 AI Usage 强制门禁仍必须按对应技能执行
