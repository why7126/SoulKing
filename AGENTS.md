---
purpose: AI Agent 工作入口
content: ProjectSoulKing 的规则加载路由、OpenSpec 红线、目录边界、验证要求和回复规范
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 00:00:00
---

# AI Agent 工作指南

## 1. 项目定位

ProjectSoulKing 是个人音乐资产管理系统，面向需要在私有环境中管理歌曲、歌词、歌单、用户资料和音频文件的个人或小团队。项目采用 FastAPI + SQLite + MinIO，前台和后台均为 `app/static/` 下的静态 Web 壳。

项目状态不得只存在于对话中。正式需求、BUG、迭代、规格、验证结果和归档记录必须沉淀到 `issues/`、`iterations/`、`openspec/`、`docs/`、`rules/` 等可审计位置。

## 2. 执行前读取路由

所有任务先读最小入口：

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/language.md
rules/agent-context-budget.md
```

按任务类型追加读取：

| 任务类型 | 追加读取 |
|---|---|
| 需求 / BUG | `rules/requirement-management.md`、`rules/bug-management.md`、`rules/issues-lifecycle.md`、对应 `issues/**/<REQ|BUG-*` |
| Sprint | `rules/iterations-lifecycle.md`、相关 `iterations/change|archive/<sprint>/` |
| OpenSpec Change | 当前 `openspec/changes/<change-id>/`、`rules/document-governance.md` |
| 文档治理 / 规范学习 | `rules/document-governance.md`、`docs/08-command-execution-order.md`、涉及长期文档时追加 `docs/standards/document-prose-hygiene.md` |
| 根因分析 / 验收返修 | `rules/root-cause-evidence.md`、`rules/bug-management.md`、`rules/testing.md` |
| 代码实现 | `rules/coding.md`、`rules/testing.md`、相关 `app/` 模块；涉及契约时追加 API、DB、UI、存储规则 |
| API 变更 | `rules/api.md`、`docs/03-api-index.md`、`app/main.py`、`app/auth_routes.py`；涉及请求日志、行为事件、链路字段或 Task Trace 时追加 `docs/standards/product-data-collection-observability.md` |
| DB / 数据模型 | `rules/database.md`、`docs/04-database-design.md`、`app/models.py`、`app/database.py`；涉及 `usage_events`、`request_logs`、`task_traces`、`task_trace_spans`、索引或保留周期时追加 `docs/standards/product-data-collection-observability.md` |
| UI / Design System | `rules/ui-design.md`、`ui-design.md`、涉及 prototype 时追加 `docs/standards/prototype-ui-acceptance.md`，以及相关 `app/static/*.css` / `*.html` / `*.js` |
| Docker / 部署 / 升级 | `rules/environment.md`、`rules/port-management.md`、`rules/release.md`、`rules/database.md`、`docs/02-deployment.md`、`docs/08-production-image-release.md`、`docker-compose.yml` |
| 对象存储 / 媒体 | `rules/data-management.md`、`rules/media.md`、`rules/object-storage.md`、`docs/07-object-storage-strategy.md`，涉及验收模板时追加 `docs/standards/media-asset-acceptance-template.md` |
| 安全 / 权限 | `rules/security.md`，以及 API、数据、部署相关规则 |
| 数据采集 / 链路观测 | `docs/standards/product-data-collection-observability.md`；涉及播放、下载、导入、日志审计、行为事件、请求封装、Task Trace、媒体链路或对象存储观测时必须声明适用层级或 N/A 原因 |

若文件不存在，应说明缺失并使用最接近的已有规则；不得编造不存在的规则内容。

## 3. Agent 工具入口

当前启用 Agent 技能入口：

```text
.agents/skills/
```

命令族覆盖 `/explore`、`/capture`、`/req-*`、`/bug-*`、`/sprint-*`、`/opsx-*`、`/spec-opt`、`/spec-study`、`/git-check`、`/release-*`、`/image-*`、`/upgrade-*`、`/usage-docs-*`、`/miniapp-*` 和项目基线命令。新增或移除 Agent 工具入口时，必须同步 `project.yaml`、`rules/directory-structure.md` 和 `scripts/validate-directory-structure.py`。其中 `/miniapp-*` 当前仅作为兼容入口保留；本项目 `project.yaml` 中 `wechat_miniapp.enabled=false` 时必须阻断执行。

## 4. 开发流程红线

- 改变业务能力、接口契约、数据结构、部署拓扑、权限边界或工作流语义时，必须先创建 OpenSpec Change。
- `openspec/specs/` 是已生效能力；除归档合并动作外不得直接修改。
- 未评审的 REQ/BUG 不得进入 Sprint 正式规划，不得 `/req-opsx`、`/bug-opsx` 或 `/sprint-apply`。
- 来源于 REQ/BUG 的 OpenSpec Change 在实现前必须纳入 `iterations/change/sprint-*`。
- 新建业务代码优先放在现有 `app/` 边界内；不得把业务代码散落到根目录。
- `.env`、真实密钥、真实用户数据、运行时数据库、临时大文件不得提交。
- 允许本地存在被 `.gitignore` 覆盖的真实 env 文件，例如 `.env`、`.env.*`、`deploy/local/*.env`、`deploy/prod/*.env`、`scripts/build-images.env`；它们的存在不作为 `/opsx-archive`、`/sprint-archive` 或目录结构校验阻断，但不得提交、不得写入 release / mintlify / archive evidence / AI Usage 产物、不得在回复或日志中展开内容。
- API 变更必须同步 OpenSpec、API 文档、相关测试和前端调用。
- DB 结构变更必须同步模型、数据库文档、迁移/兼容说明和测试。
- API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测相关变更必须读取 `docs/standards/product-data-collection-observability.md`，并在 REQ、Change、Sprint 或验收材料中声明 `product_data_collection_observability` 适用层级、N/A 原因和验证摘要。
- UI 变更必须遵守 `ui-design.md` 与 `rules/ui-design.md`。
- 命令推荐与执行顺序必须遵守 `docs/08-command-execution-order.md`；已评审 REQ/BUG 必须先纳入 Sprint，再转 OpenSpec。
- `/spec-study` 学习对象存在 `docs/spec-logs/CHANGELOG.md` 时，应按“日志索引 → 单次学习/治理日志 → 真实治理资产 → 必要脚本补证”的顺序学习；日志只作为入口地图，不替代当前资产、OpenSpec Change、Sprint 四件套或正式规格事实源。
- 长期文档、规则和技能说明不得写入会话推理、临时草稿、review 对话、不可解析引用、未脱敏本机路径或学习对象源码。
- 推送或交付前建议运行 `/git-check`；发现真实 env、运行时数据、密钥、本机路径或大文件时必须先处理。

## 5. 状态同步

工作流状态变化后运行：

```bash
python scripts/sync-workflow-status.py --event <event> [--req REQ-xxxx] [--bug BUG-xxxx] [--change change-id] [--sprint sprint-xxx|auto]
```

归档涉及 Issue 物理阶段迁移时继续运行：

```bash
python scripts/promote-issue-stage.py --to archive [--change change-id] [--sprint sprint-xxx] --reason "<event>"
```

发布版本若涉及公开产品手册，必须以 `releases/<version>/usage-docs/manifest.json` 为事实源，运行：

```bash
python scripts/generate-usage-docs.py <version>
python scripts/validate-usage-docs.py --release-dir releases/<version>
```

`mintlify/` 仅作为公开站点源目录和投影结果，不得替代 release 快照事实源。

## 5.1 命令完成输出契约

所有 `.agents/skills/*/SKILL.md` 命令技能完成时，最终回复必须包含「下一步」与「待用户决策/处理」两项真实结果，不得把契约规则、尖括号占位符、通用示例或 `MUST/SHOULD` 规范语气原样输出给用户。

- 「下一步」承载可复制执行的命令或明确动作。
- 若当前没有可推进动作，「下一步」写“暂无可推进下一步”。
- REQ 链路使用原始 `REQ-*`，BUG 链路使用原始 `BUG-*`；REQ/BUG 来源的后续 `/opsx-apply`、`/opsx-archive` 也使用原始 REQ/BUG ID。
- 「待用户决策/处理」只列额外缺失输入、范围/策略选择、证据补充、验收/发布确认、阻塞项或人工处理事项。
- 已在「下一步」中给出的命令或动作不得重复写入「待用户决策/处理」。
- 若「下一步」已经给出唯一可执行命令且无额外人工事项，「待用户决策/处理」写“无”；不得再要求用户确认是否执行同一个命令。
- 不得因为输出下一步引导而自动执行下一命令，除非用户明确授权。

## 5.2 完成检查清单

```text
□ 是否遵守 OpenSpec Change 流程
□ 已评审 REQ/BUG 是否先纳入 sprint-xxx 后再 req/bug-opsx
□ 所有 Change 是否已纳入某个 sprint-xxx 后再 opsx-apply
□ 是否更新 issues / openspec / iterations / docs / releases（按需）
□ 是否运行 Workflow Sync（状态变化时）
□ 是否补充或更新 tests（按需）
□ 是否同步 API / DB / .env.example / deploy / Mintlify（按需）
□ 是否触发产品数据采集与链路观测门禁，且已声明 `product_data_collection_observability` 适用性、affected_layers、N/A 原因和 validation 摘要
□ 是否遵守目录结构与禁止目录
□ 是否避免真实 env、密钥、运行时数据进入 release / Mintlify / archive evidence / AI Usage
□ 是否完成必要校验：目录结构、OpenSpec、Agent 上下文预算、Mintlify、release、测试或 Docker（按需）
□ 命令输出是否包含去重后的下一步与待用户决策/处理
```

## 6. 输出要求

回复默认使用简体中文。涉及代码时说明修改文件、影响面、验证命令、未运行验证的原因，以及是否影响 API、数据库、UI、部署、安全或跨模块契约。
