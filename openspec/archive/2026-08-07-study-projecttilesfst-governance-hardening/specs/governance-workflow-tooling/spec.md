## ADDED Requirements

### Requirement: 跨项目治理学习应用

本项目 MUST 支持 `/spec-study` 以两阶段方式学习外部 Harness / OpenSpec / Agent 治理工程，并在用户确认后才将候选学习内容应用到本项目治理资产。

#### Scenario: 学习对象只读

- **WHEN** `/spec-study` 学习本地或远端项目
- **THEN** 学习对象 MUST 全程只读
- **AND** 不得在学习对象路径内写入、安装依赖、格式化、迁移、修复测试、清理、提交、重置或修改 Git 状态

#### Scenario: 应用阶段项目化改写

- **WHEN** 用户确认应用学习内容
- **THEN** 应用内容 MUST 按 ProjectSoulKing 的 `app/`、`app/static/`、SQLite、MinIO、Mintlify `docs.json` 和 `.agents/skills/` 边界重写
- **AND** 不得原样复制 ProjectTilesFST 的业务专属规则、脚本或源码语境

### Requirement: 治理上下文预算

本项目 MUST 通过规则和脚本约束 Agent 的读取范围、摘要复用、宽泛搜索和命令输出契约。

#### Scenario: 命令 Skill 校验

- **WHEN** 运行 `python scripts/validate-agent-context-budget.py`
- **THEN** 所有命令 Skill MUST 引用 `rules/agent-context-budget.md`
- **AND** MUST 包含摘要复用、force-proceed follow-up、最终输出契约、Sprint 门禁和 REQ/BUG 后续参数规范

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
