---
purpose: TilesFST 治理升级学习应用报告
content: 版本升级路径、证据化根因、音乐媒体验收模板和文档索引补强
created_at: 2026-08-21 22:50:52
updated_at: 2026-08-21 22:50:52
---

# TilesFST 治理升级学习应用报告

## 学习对象与模式

- 学习对象：ProjectTilesFST。
- 学习模式：Phase 1 只读学习，Phase 2 经用户确认后应用 `U1`、`R1`、`M1`、`D1`。
- 执行时间：2026-08-21 22:50:52，时区 `Asia/Shanghai`。
- 应用 Change：`apply-tilesfst-governance-upgrade-learnings`。
- 承载 Sprint：`sprint-001`。

## 学习到的治理能力

- 版本升级路径事实源：区分目标版本 release / image manifest 与 `from_version -> to_version` 升级路径证据。
- 证据化根因：以 `unknown`、`hypothesis`、`probable`、`confirmed` 表达根因证据强度。
- 媒体验收模板：用固定维度记录对象 key、对象存在性、访问结果、元数据和端上展示。
- 文档索引分层：让 standards、rules、spec logs 和命令入口更容易检索。

## 已采纳内容和采纳原因

| 内容 | 采纳原因 | 落地位置 |
|---|---|---|
| 版本升级路径治理 | ProjectSoulKing 已有 release 与镜像证据，但缺少升级路径支持级别、备份、回滚和 smoke 事实源 | `scripts/validate-release-upgrade.py`、`.agents/skills/upgrade-*`、`rules/release.md`、`docs/02-deployment.md`、`docs/08-production-image-release.md` |
| 证据化根因治理 | BUG 和返修链路需要区分证据强度，减少把推测写成确认根因的风险 | `rules/root-cause-evidence.md`、`scripts/validate-root-cause-evidence.py`、BUG / opsx / workflow 技能入口 |
| 音乐媒体资产验收模板 | 音频、歌词、封面、头像和 MinIO 链路需要统一验收记录口径 | `docs/standards/media-asset-acceptance-template.md`、`rules/media.md`、`rules/object-storage.md`、`docs/07-object-storage-strategy.md` |
| 文档索引补强 | 新增 standards 与命令族需要出现在入口索引和目录校验中 | `docs/README.md`、`DOCUMENT_METADATA_INDEX.md`、`AGENTS.md`、`project.yaml`、`scripts/validate-directory-structure.py` |

## 未采纳内容和原因

- 未采纳 TilesFST 的 MySQL / COS / 小程序 / SKU / 证书专用规则：ProjectSoulKing 当前事实是 SQLite、MinIO 单桶、音频/歌词/封面/头像。
- 未复制学习对象脚本原文：升级脚本已按 SoulKing 的 `SOULKING_IMAGE_TAG`、SQLite 备份、MinIO 对象存储和单应用镜像重写。
- 未引入业务运行时代码：本次为治理应用，不修改 `app/`、`app/static/` 或 `packaging/`。

## 替代方案或取舍

- 升级脚本先作为计划与校验工具，不自动实施升级，避免治理命令越过人工运维授权。
- 根因证据脚本采用轻量启发式校验，先发现缺失状态和 confirmed 缺证据问题，不自动改写 BUG 文档。
- 媒体验收模板只规定证据结构，不扩大为新媒体处理能力。

## 验证责任和后续触发条件

- 发布或部署升级前，由 `/upgrade-plan` 与 `/upgrade-validate` 生成并校验具体路径证据。
- BUG、返修或测试失败涉及根因判断时，由对应命令运行 `validate-root-cause-evidence.py` 的聚焦校验。
- 媒体相关 REQ、BUG、Change、Sprint 或 release 触达音频、歌词、封面、头像或对象存储时，引用媒体资产验收模板。

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `.agents/skills/upgrade-plan/SKILL.md`、`.agents/skills/upgrade-validate/SKILL.md` | 新增升级计划与校验命令入口 |
| `scripts/validate-release-upgrade.py` | 新增升级路径计划生成和校验脚本 |
| `rules/release.md`、`rules/environment.md`、`rules/database.md`、`rules/security.md` | 补充升级路径、env diff、SQLite 备份和公开安全边界 |
| `docs/02-deployment.md`、`docs/08-production-image-release.md` | 补充部署升级计划和镜像证据关系 |
| `rules/root-cause-evidence.md`、`scripts/validate-root-cause-evidence.py` | 新增根因证据规则和轻量校验 |
| `.agents/skills/{bug-complete,explore,opsx-apply,opsx-modify,workflow-sync}/SKILL.md`、`rules/{bug-management,testing}.md`、`docs/standards/testing-governance.md` | 接入根因证据门禁 |
| `docs/standards/media-asset-acceptance-template.md`、`rules/media.md`、`rules/object-storage.md`、`docs/07-object-storage-strategy.md` | 新增并引用音乐媒体资产验收模板 |
| `AGENTS.md`、`project.yaml`、`rules/directory-structure.md`、`scripts/validate-directory-structure.py`、`DOCUMENT_METADATA_INDEX.md`、`docs/README.md`、`docs/08-command-execution-order.md` | 同步命令入口、目录边界、文档索引和校验矩阵 |
| `openspec/changes/apply-tilesfst-governance-upgrade-learnings/`、`iterations/change/sprint-001/` | 承载本次治理应用的 Change 与 Sprint scope |

## 影响范围

- API：不影响运行时接口。
- 数据库：不修改 schema；新增 SQLite 升级备份和 smoke 证据要求。
- 前台 Web：不修改运行时页面；新增媒体验收记录口径。
- 后台管理端：不修改运行时页面；新增媒体验收记录口径。
- 桌面封装：不影响。
- 对象存储：不修改实现；新增 MinIO 对象证据、访问 smoke 和回滚边界要求。
- Docker Compose：不修改拓扑；新增升级计划对 Compose/env 示例的校验要求。
- 测试：新增两个治理脚本，后续按触达范围运行。

## 校验命令和结果

- `python -m py_compile scripts/validate-release-upgrade.py scripts/validate-root-cause-evidence.py`：通过。
- `python scripts/validate-release-upgrade.py env-diff`：通过；输出仅包含变量名、分类和建议。
- `python scripts/validate-release-upgrade.py --root <tmp-root> plan --from fresh --to v0.1.0`：通过，生成临时首次部署计划。
- `python scripts/validate-release-upgrade.py validate-plan --plan <tmp-root>/releases/v0.1.0/upgrade-plans/fresh-to-v0.1.0.json`：通过。
- `python scripts/validate-root-cause-evidence.py --change apply-tilesfst-governance-upgrade-learnings --json`：通过；本 Change 未关联 BUG，根因证据校验不适用。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate apply-tilesfst-governance-upgrade-learnings`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-tilesfst-governance-upgrade-learnings`：通过。
- `python scripts/validate-doc-prose-hygiene.py <focused-paths>`：通过执行，返回 10 条 warning；命中项为既有规则和新增说明中的启发式历史叙事词，不作为 blocker。
- `python scripts/validate-doc-governance.py`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-governance-upgrade-learnings --sprint auto`：通过，解析 Sprint 为 `sprint-001`，Errors 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-tilesfst-governance-upgrade-learnings --sprint sprint-001 --json`：执行成功，`status=warning`、`usage_mode=unavailable`、`warning_count=1`；原因是当前会话没有可用 token_count 事件，非父命令阻塞。

## 学习对象只读保护结果

对 ProjectTilesFST 仅执行只读扫描、片段读取和 Git 状态查询；未在学习对象路径中执行写入、安装、生成、格式化、迁移、测试修复、清理、提交、切换分支或修改 Git 状态的操作。

## 后续建议

- 可在首个正式 release 产生后，用 `/upgrade-plan --from fresh --to <version>` 生成首次部署计划样例。
- 若后续媒体类 BUG 频繁出现，可把媒体资产验收模板进一步接入 BUG archive readiness。
