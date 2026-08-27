## MODIFIED Requirements

### Requirement: Agent 治理命令必须提供可校验的流程门禁

Agent 治理命令 MUST 通过项目规则、技能文档和校验脚本约束命令顺序、Sprint Inclusion Gate、上下文预算、学习对象只读保护、Git 安全检查和最终输出契约。

#### Scenario: 跨项目治理学习应用

- **GIVEN** 用户确认应用其他项目的治理经验
- **WHEN** `/spec-study apply` 修改治理资产
- **THEN** 变更 MUST 有 active OpenSpec Change
- **AND** 该 Change MUST 已纳入 Sprint scope
- **AND** 学习对象 MUST 只读
- **AND** 本项目 MUST 生成一份 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md` 学习报告

#### Scenario: 推送前安全检查

- **GIVEN** 用户运行 `/git-check`
- **WHEN** 仓库存在 staged 或 tracked 的真实 env、运行时数据、密钥、本机绝对路径或不应提交的大文件
- **THEN** 命令 MUST 返回非零并输出脱敏修复建议
- **AND** 命令 MUST NOT 自动修改、删除或取消暂存任何文件
