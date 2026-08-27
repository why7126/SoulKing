## ADDED Requirements

### Requirement: Agent 治理命令必须提供可校验的流程门禁

Agent 治理命令 MUST 通过项目规则、技能文档和校验脚本约束命令顺序、Sprint Inclusion Gate、上下文预算、学习对象只读保护、Git 安全检查、文档治理检查、最小相关验证选择和最终输出契约。

#### Scenario: 跨项目治理学习应用

- **GIVEN** 用户确认应用其他项目的治理经验
- **WHEN** `/spec-study apply` 修改治理资产
- **THEN** 变更 MUST 有 active OpenSpec Change
- **AND** 该 Change MUST 已纳入 Sprint scope
- **AND** 学习对象 MUST 只读
- **AND** 本项目 MUST 生成一份 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md` 学习报告

#### Scenario: 文档治理检查

- **GIVEN** 治理变更新增或修改长期 Markdown、规范工程日志或 Agent 入口文档
- **WHEN** 运行 `python scripts/validate-doc-governance.py`
- **THEN** 校验 MUST 检查长期 Markdown frontmatter、脚手架残留、spec-log 隐私路径和 AGENTS 字数预算
- **AND** 校验 MUST NOT 自动修改文件

#### Scenario: 最小相关验证选择

- **GIVEN** Change 修改治理资产、脚本、API、DB、UI、部署或安全边界
- **WHEN** Agent 输出验证结果
- **THEN** 结果 MUST 说明已运行验证与影响面的对应关系
- **AND** 未运行的高相关验证 MUST 说明原因
