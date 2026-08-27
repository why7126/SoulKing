---
purpose: 跨项目治理学习报告
content: 记录应用 TilesFST 数据采集治理学习项 D1-D4 的采纳内容、影响范围和验证结果
created_at: 2026-08-27 00:43:58
updated_at: 2026-08-27 00:55:00
---

# TilesFST 数据采集治理学习报告

## 学习对象

- 学习对象：`<Projects>/ProjectTilesFST/ProjectTilesFST`
- 学习模式：`auto`，聚焦内容：`数据采集`，应用项：`D1,D2,D3,D4`
- 执行时间：`2026-08-27 00:43:58`，时区：`Asia/Shanghai`

## 学习到的治理能力

- 数据采集规范应区分行为事件、请求日志、任务链路和流程节点，避免把观测数据混成无边界日志。
- 采集规范需要在 AGENTS、rules、技能和校验脚本中形成门禁，而不是只作为参考文档。
- 触发范围内的 REQ、Change、Sprint 和验收材料应记录结构化声明，N/A 也必须说明原因。
- 校验脚本应聚焦 active Change、REQ、Sprint 或 diff，避免默认扫描全部历史归档。

## 已采纳内容

| 项 | 内容 | 采纳原因 |
|---|---|---|
| D1 | SoulKing 版产品数据采集与链路观测标准 | 本项目缺少播放、下载、导入、歌词、歌单、媒体和对象存储观测的统一治理事实源。 |
| D2 | AGENTS、rules 和文档索引门禁 | 入口规则需要把相关 API、DB、媒体和请求封装变更路由到采集标准。 |
| D3 | req、opsx、sprint 技能声明检查 | 命令执行阶段需要提醒并阻断缺声明、缺 N/A 原因或缺验证摘要的相关变更。 |
| D4 | 标准校验、门禁校验和聚焦测试 | 脚本化校验可以防止采集规范只停留在文档提醒。 |

## 未采纳内容

- 未采纳 TilesFST 的瓷砖、店主端、小程序、Orval、MySQL 生产语境。
- 未采纳业务采集实现、数据库表创建、前后台请求封装改造或第三方埋点平台接入。
- 未批量修复历史归档 Change、历史 Issue 或历史 Sprint 的采集声明。

## 替代方案与取舍

- 先落治理标准和流程门禁，后续业务采集能力单独通过 REQ / OpenSpec Change 排期。
- 标准文档承载详细字段和验收口径，入口文件只写路径引用与门禁摘要，避免事实源漂移。
- 校验脚本默认聚焦指定目标，减少历史归档噪音；需要全局治理时再通过独立命令扩展。

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `docs/standards/product-data-collection-observability.md` | 新增 SoulKing 数据采集与链路观测标准。 |
| `docs/README.md` | 增加标准文档索引。 |
| `AGENTS.md` | 接入任务读取路由、红线和完成检查清单。 |
| `rules/api.md` | 增加 API 相关采集门禁。 |
| `rules/database.md` | 增加日志表、索引、保留周期和观测字段门禁。 |
| `rules/testing.md` | 增加采集相关验证要求。 |
| `rules/data-management.md` | 增加采集数据安全和脱敏边界。 |
| `rules/document-governance.md` | 明确采集标准事实源归属。 |
| `rules/requirement-management.md` | 增加需求阶段声明要求。 |
| `rules/iterations-lifecycle.md` | 增加 Sprint 阶段复核要求。 |
| `docs/08-command-execution-order.md` | 增加采集门禁校验矩阵。 |
| `.agents/skills/req-*.md` | 在需求生成、完善、评审和转 Change 阶段增加声明检查。 |
| `.agents/skills/opsx-*.md` | 在 propose、apply、modify、archive 阶段增加采集门禁。 |
| `.agents/skills/sprint-*.md` | 在 Sprint 规划、执行和归档阶段增加采集门禁。 |
| `scripts/validate-product-data-observability-standard.py` | 新增标准完整性校验。 |
| `scripts/validate-product-data-observability-gates.py` | 新增入口和目标声明门禁校验。 |
| `tests/test_product_data_observability_gates.py` | 覆盖采集门禁脚本关键路径。 |
| `openspec/changes/apply-tilesfst-data-collection-governance-learnings/` | 承载本次 proposal、design、tasks、delta spec 和 trace。 |
| `iterations/change/sprint-001/` | 将本 Change 纳入 Sprint scope 并刷新派生文档。 |

## 产品影响

- API：本次不修改业务接口；后续相关变更需声明采集适用性或 N/A。
- 数据库：本次不修改模型或 schema；后续日志、事件、任务链路、索引和保留周期变更需触发门禁。
- 前台 Web：本次不修改 `app/static/`。
- 后台管理端：本次不修改 `app/static/`。
- 桌面封装：不影响。
- 对象存储：本次不迁移对象或改存储实现；后续媒体链路和对象观测变更需触发门禁。
- Docker Compose：不影响。
- 测试：新增治理脚本测试。

## 校验命令和结果

- `python -m py_compile scripts/validate-product-data-observability-standard.py scripts/validate-product-data-observability-gates.py`：通过。
- `uv run pytest tests/test_product_data_observability_gates.py`：通过，4 passed。
- `python scripts/validate-product-data-observability-standard.py`：通过。
- `python scripts/validate-product-data-observability-gates.py --change apply-tilesfst-data-collection-governance-learnings`：通过，Change 声明存在。
- `python scripts/validate-product-data-observability-gates.py --sprint sprint-001`：通过，Sprint 聚焦扫描声明存在。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `openspec validate apply-tilesfst-data-collection-governance-learnings --strict`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-tilesfst-data-collection-governance-learnings`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-doc-prose-hygiene.py <focused-paths>`：退出码 0，报告 2 条既有命令顺序文本启发式 warning。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-data-collection-governance-learnings --sprint auto`：通过，解析 Sprint 为 `sprint-001`。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-tilesfst-data-collection-governance-learnings --sprint sprint-001 --json`：通过，`usage_mode=actual`，Sprint snapshot 已刷新。

## 学习对象只读保护

学习对象只执行读取、搜索和 `git status --short`；未在学习对象路径执行写入、安装、格式化、迁移、测试修复、提交、重置或清理操作。学习对象本身存在既有未提交变更，本次未改动。

## 后续建议

- 后续若要实现播放事件、下载日志、导入任务 trace 或后台日志审计，应先走独立 REQ / OpenSpec Change。
