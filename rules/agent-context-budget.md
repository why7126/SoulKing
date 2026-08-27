---
purpose: Agent 上下文预算
content: 任务读取顺序、最小上下文和防止无差别扫仓库规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 00:00:00
---

# Agent 上下文预算

- 先读 `AGENTS.md`、`project.yaml`、相关 `rules/` 和目标文件，再决定实现。
- 搜索优先使用 `rg` / `rg --files`。
- 不为简单任务全量读取 `openspec/archive/`、`node_modules/`、`data/` 或大文件。
- 涉及 UI 时读取 `ui-design.md` 和目标 HTML/CSS/JS。
- 涉及存储时读取 `app/storage.py`、`.env.example`、`docs/07-object-storage-strategy.md`。
- 当前命令 Skill、共用 Skill（如 `.agents/skills/workflow-sync/SKILL.md`）以及 `.agents/skills/{req,bug,opsx,sprint,release,image,build}-*`、`.agents/skills/capture`、`.agents/skills/explore`、`.agents/skills/spec-opt`、`.agents/skills/spec-study`、`.agents/skills/initialize-project` 应按需读取；同一会话已读且无变更时用摘要承接，不重复全量读取。
- 已读摘要复用应至少包含：路径、版本线索（`updated_at`、mtime、hash 或本会话读取时间）、与当前任务相关的规则摘要、适用范围、需要补读的原因。摘要不得写入仓库，不得持久化系统/developer 指令、完整工具输出、密钥、Cookie、Authorization header、`.env` 内容或真实用户数据。
- 以下情况必须补读目标文件或必要片段：文件版本线索变化、用户要求复核原文、任务升级到 apply/archive/release/upgrade/req-opsx/bug-opsx/sprint-propose 等高风险阶段、涉及安全/API/DB/部署/Workflow Sync/AI Usage、摘要不足以覆盖当前门禁或校验失败。
- 大范围搜索默认排除：`.git/`、`node_modules/`、`dist/`、`coverage/`、`openspec/archive/`、`openspec/changes/archive/`、`data/`、运行时上传目录、构建产物和依赖目录。分析 Harness/Agent 资产时 MAY 放开 `.agents/`、`.cursor/`、`.codex/`、`.kiro/`、`.opencode/`、`.claude/`，但必须先说明原因并优先输出清单或命中数。
- `/spec-opt` 规范优化命令只修改治理资产，覆盖 `.agents/skills`、`rules/`、`docs/`、`scripts/`、`AGENTS.md` 和 active OpenSpec Change 的同步矩阵；禁止修改 `app/`、`app/static/` 或 `packaging/` 业务代码。完成规范、技能、脚本、目录边界或校验规则迭代后，MUST 写入 `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md` 治理迭代日志。
- `/spec-study` 跨项目 Harness 学习应用命令 MUST 先学习并输出候选内容，等待用户确认后再应用；学习范围横向覆盖项目入口、`rules/`、`docs/`、多 Agent 目录、`scripts/`、部署与环境示例。学习对象全程只读且绝不允许被改动；应用阶段遵守 active OpenSpec Change 与 Sprint Inclusion Gate，并禁止修改 `app/`、`app/static/` 或 `packaging/` 业务代码。
- `/spec-study` 同一次学习应用流程只生成一份正式学习报告，统一写入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md`，并承载本次学习触发的治理资产应用结果；不得额外生成内容重复的 `YYYYMMDDhhmmss-governance-xxx.md`。
- `docs/spec-logs/` 不得包含用户隐私数据、真实客户数据、密钥、访问令牌、本机绝对路径、未脱敏日志、聊天原文、工单原文、截图中的个人信息或学习对象源码；涉及路径证据时 MUST 使用仓库相对路径或 `<local-project>`、`<user-home>` 等脱敏占位符。
- 若学习对象存在 `docs/spec-logs/CHANGELOG.md`，`/spec-study` SHOULD 按“日志索引 → 单次 study/governance 日志 → 真实治理资产 → 必要脚本补证”的顺序学习；日志只作为入口地图，不替代当前资产、OpenSpec Change、Sprint 四件套或正式规格事实源。
- 命令顺序、下一步参数和串行写入边界 MUST 遵守 `docs/08-command-execution-order.md`。REQ/BUG 来源链路在 `/opsx-*` 下一步中继续使用完整 `REQ-xxxx-slug` / `BUG-xxxx-slug`；无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。
- 命令最终输出契约 MUST 区分「下一步」与「待用户决策/处理」：技能文件不得提供可被原样输出的尖括号占位模板或与当前命令无关的通用示例；已在「下一步」中给出的命令或动作不得重复写入「待用户决策/处理」；后者只列缺失输入、范围/策略选择、证据补充、验收/发布确认、生产实施确认、阻塞项或人工处理事项，没有则写“无”。
- `/git-check` 用于推送前安全检测。成功路径只报告扫描摘要；失败路径只输出脱敏命中和修复建议，不得展开真实 env、密钥、Token、Cookie、连接串或个人路径原文。
- `/upgrade-plan` 与 `/upgrade-validate` 用于生成和校验 release 升级路径计划；只读取目标 release、image manifest、env 示例和必要中间版本摘要，不得读取真实 env 或自动执行生产升级、SQLite restore、对象存储写入维护。
- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；未获明确授权时只输出可复制 capture 文案并说明“未自动创建 Issue”。
- `scripts/validate-agent-context-budget.py` 用于检查命令技能是否引用本规则，并阻止常见宽泛读取、最终输出占位模板、通用示例、重复诱因和规范语气泄漏风险回退。
