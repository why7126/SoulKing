---
purpose: 发布规范
content: ProjectSoulKing 发布前检查、镜像证据、迁移、验证和公告要求
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 发布规范

发布前必须完成测试、OpenSpec 校验、接口文档同步、变更归档、镜像证据判断、产品手册决策和发布说明。

## 产品版本发布对象

产品版本发布对象用于表达一次对外产品发版，放入：

```text
releases/vX.Y.Z/release.json
```

发布对象 MUST 支持：

- 一个产品版本关联一个或多个 Sprint。
- 追踪关联 REQ、BUG 和 OpenSpec Change。
- 区分 Sprint `release-note.md` 与产品版本公告：Sprint release note 描述迭代交付，产品版本公告描述对外版本。
- 阻止未评审、未纳入交付或未归档闭环的内容进入正式发布范围。

## 公开发布公告

公开发布公告源文件放入：

```text
releases/vX.Y.Z/announcement.mdx
```

发布公告 MUST：

- 面向公开页面展示。
- 可通过 Mintlify build / preview 或等价静态 MDX 校验。
- 可纳入 Git Review。
- 不依赖后端运行时 API 或数据库才能展示。
- 包含版本号、发布时间、关联 Sprint、新增功能、修复 BUG、发布注意事项、已知问题、升级步骤、回滚说明和影响范围。
- 不泄露密钥、真实用户数据、内部数据库连接串、MinIO 凭据、不可公开域名或敏感运维信息。

## 公开产品手册

公开产品手册事实源放入：

```text
releases/vX.Y.Z/usage-docs/
releases/vX.Y.Z/usage-docs/manifest.json
```

`mintlify/` 是公开站点源目录和投影结果，不是版本事实源。生成和投影 MUST 通过：

```bash
python scripts/generate-usage-docs.py <version>
python scripts/validate-usage-docs.py --release-dir releases/<version>
python scripts/validate-mintlify-site.py
```

发布对象 `usage_docs.status` MUST 是：

- `pending_confirmation`：尚未确认是否需要产品手册，阻断发布准备。
- `generated`：已生成版本化手册，必须通过截图覆盖、manifest、Mintlify 投影和公开安全校验。
- `skipped`：明确确认本版本不需要产品手册，必须记录确认人、时间和原因，且不得创建空 `usage-docs/`。

生成前 MUST 在 `release.json` 写入 `usage_docs.generation_decision`；不得仅凭对话或代码变更推断需要生成。生成后的每个用户可见页面 MUST 引用至少一张真实系统截图，截图集中放在 `mintlify/assets/screenshots/`，并在 manifest 中记录 `site_asset`、`content_hash`、覆盖页面、来源和复用原因。

当前版本 usage docs SHOULD 以前一个已生成 usage docs 的产品版本为完整基线。若 `releases/<previous>/usage-docs/manifest.json` 存在，则新版本 `manifest.pages` SHOULD 覆盖前一版本全部页面，并在 `source_version`、`input_files` 或 `manual_overrides` 中记录继承来源；除非用户明确授权页面下线或内容收敛，否则不得退回只包含模板页、增量页或当前 Sprint 页的文档集。

已发布旧版本 usage docs 默认是发布快照。自动化在无明确授权时 MUST NOT 改写旧版本产品行为说明、操作步骤、功能可用性、版本差异或已知问题历史语义。broken links、Mintlify 配置迁移、frontmatter/manifest 补齐、格式修复、导航引用修复、敏感信息移除和目录结构迁移等非内容性维护 MAY 自动执行，但 MUST 记录维护范围。旧版本内容性更正 MUST 记录原因、确认来源、时间、文件范围和变更说明。

`域名/docs` 是部署边界，不由 release 源文件单独完成。项目 MUST 记录采用 Mintlify base path、静态 CDN、Nginx 反向代理或等价方案；若方案未确认，`/release-prepare` MUST 记录 blocker 或待确认项。

## 版本升级路径治理

发布治理 MUST 区分“目标版本已发布”和“某条升级路径已验证”。`releases/<version>/release.json`、`image-build-plan.json`、`image-manifest.json` 表达目标版本事实；升级路径 MUST 额外表达 `from_version -> to_version` 的来源版本、支持级别、执行步骤、验证证据和回滚证据。

升级路径计划默认放在：

```text
releases/<to-version>/upgrade-plans/<from-version>-to-<to-version>.json
```

`from_version=fresh` 表示首次部署。升级计划 MUST 至少包含：

- `from_version`、`to_version`、`support_level`、`source_confidence`。
- `version_facts`：目标 release、目标 image manifest、部署 `SOULKING_IMAGE_TAG` 摘要。
- `impact_summary`：SQLite 数据、env、Docker、API、对象存储和维护任务影响。
- `env_diff`：只输出变量名、分类、说明和建议，不输出真实 env 值。
- `required_checks`、`steps`、`rollback`、`blockers`、`warnings`、`evidence`。

支持级别含义：

| 支持级别 | 含义 |
|---|---|
| `fresh-install-supported` | 目标版本支持空环境首次部署。 |
| `adjacent-upgrade-supported` | 支持从上一发布版本升级到目标版本。 |
| `cross-version-upgrade-supported` | 支持从指定旧版本跨多个版本升级到目标版本，且已有完整演练与回滚证据。 |
| `cross-version-upgrade-requires-manual-review` | 跨版本升级理论上可规划，但缺少完整演练、中间版本事实源或存在 SQLite/env/object storage 等人工复核项。 |
| `unsupported` | 不支持直接升级，需要专项迁移、先升中间版本或人工方案。 |

缺少中间版本 release 事实源、缺少跨版本演练、缺少 SQLite 备份/恢复、缺少 env diff、缺少对象存储审计或缺少回滚证据时，MUST NOT 将跨版本升级标记为 `cross-version-upgrade-supported`。

推荐命令：

```text
/upgrade-plan --from <fresh|version> --to <version>
/upgrade-validate --plan releases/<version>/upgrade-plans/<from>-to-<version>.json
python scripts/validate-release-upgrade.py plan --from <fresh|version> --to <version>
python scripts/validate-release-upgrade.py validate-plan --plan releases/<version>/upgrade-plans/<from>-to-<version>.json
```

upgrade 命令只生成计划和校验结果，MUST NOT 自动执行生产升级、自动修改真实生产 env、自动执行 SQLite restore、写入型 migration 或对象存储写入维护任务。

## 发布前门禁

发布确认前 MUST 校验：

| 门禁 | 要求 |
|---|---|
| OpenSpec | 关联 Change 已 archive，相关能力已合并到 `openspec/specs/`；未归档项不得进入正式发布范围 |
| 测试 | 按变更范围执行并记录 pytest / E2E / smoke 结果 |
| API | 涉及 API 变更时，FastAPI OpenAPI、`docs/03-api-index.md` 和 `app/static/*.js` 调用已同步 |
| Docker Compose | 涉及部署变更时，Compose 配置与部署文档已同步 |
| 数据库 | 涉及数据库模型或迁移影响时，SQLAlchemy 模型、启动兼容迁移、数据库文档、SQLite 备份或回滚说明已同步 |
| 环境变量 | 涉及环境变量时，`.env.example` 与相邻注释已同步 |
| 产品版本 | 若项目暴露 `PRODUCT_VERSION`，必须与发布对象版本一致；如不更新，必须记录原因 |
| Mintlify | 公告 build / preview 或等价校验通过 |
| 产品手册 | `usage_docs` 决策完成；需要手册时 `usage-docs/manifest.json`、截图覆盖和 Mintlify 投影校验通过 |
| Mintlify 多版本站点 | generated usage docs 已同步或投影到 `mintlify/`，导航、`latest`、公告投影、共享截图 hash 和公开安全校验通过；未确认生产承载方式时记录 blocker 或待确认项 |
| 镜像准备 | 当 `image_required=true` 时，`releases/<version>/image-build-plan.json` 已生成、校验通过并被 `release.json` 引用 |
| 镜像构建 | 当 `image_required=true` 或包含离线镜像交付时，`releases/<version>/image-manifest.json` 已生成、未过期并被 `release.json` 引用；外部构建证据必须受控 |

任一必填门禁失败时，发布流程 MUST 阻断，并输出失败原因与修复建议。

当发布范围涉及后端运行代码、静态 Web 壳、Dockerfile、Compose、`.env.example`、镜像构建脚本、构建 env 示例、数据库模型/迁移、API 文档/前端调用或离线镜像交付时，发布对象 MUST 将 `image_required` 设为 `true`，并按以下顺序执行：

```text
/release-propose <version>
  -> /release-prepare <version>
  -> /image-prepare <version>
  -> /image-build <version>
  -> /release-publish <version>
```

`/image-prepare` 只生成或更新 `releases/<version>/image-build-plan.json`，记录版本、image tag、source scope、build env 安全摘要、Dockerfile、Compose、构建脚本、构建 env 示例、SQLAlchemy 模型/启动兼容迁移、数据库文档 input hash、required commands、auto actions、warnings 和 blockers。默认构建 env 缺失或 `IMAGE_BUILD_TAG` 与版本不一致时，命令 MAY 只自动创建/更新安全白名单变量并记录 auto action。Compose fallback tag 与当前版本不同但实际发布 env 明确设置 `SOULKING_IMAGE_TAG=<version>` 时 SHOULD 记录 warning，不得作为 blocker 要求每次 release 改 Compose 默认值。

`/image-build` MUST 读取有效且未过期的 image build plan 后再复用 `scripts/build-images.sh` 执行真实构建。构建成功后写入 `releases/<version>/image-manifest.json`，记录 version、image_tag、built_at、platform、app_image、tarball、input_hashes、validation 和 source_plan。镜像 tar 包与 `.sha256` 默认输出到 `releases/<version>/images/`，不得包含真实密钥或数据库文件。缺少 plan、plan blocked、版本/tag 不一致、input hash 漂移、Docker/buildx/网络/基础镜像源/验证/tar/sha256 失败时 MUST 阻断，不得伪造成功 manifest。

发布确认阶段 MUST 重新校验 manifest 的版本、tag、source plan 和 input hashes。manifest 生成后 Dockerfile、构建脚本、数据库模型/迁移、Compose 或 release input 漂移时，镜像证据失效，必须重新执行 `/image-prepare` 与 `/image-build`，或记录经批准的外部构建证据。

外部构建证据只可作为受控替代证据，必须记录来源、版本、image tag、平台、镜像 digest 或 tarball sha256、校验方式、负责人确认和风险说明；不得绕过公开安全扫描、版本一致性校验或 input hash 漂移校验。

## 发布命令族

发布命令族以 `.agents/skills/release-*` 与 `.agents/skills/image-*` 为入口；新增或修改发布命令时 MUST 更新 `.agents/skills/`。

推荐命令：

| 命令 | 目标 |
|---|---|
| `/release-propose <version>` | 创建或更新产品版本发布计划，选择关联 Sprint / REQ / BUG / Change |
| `/release-prepare <version>` | 执行发布前校验，生成或更新公告源文件 |
| `/image-prepare <version>` | 生成镜像构建计划并校验 release、tag、Compose、Dockerfile、数据库模型/迁移等输入 |
| `/image-build <version>` | 基于有效构建计划执行真实镜像构建、验证、离线包导出并生成 manifest |
| `/upgrade-plan --from <fresh|version> --to <version>` | 生成首次部署、相邻升级或跨版本升级与回滚计划 |
| `/upgrade-validate --plan <path>` | 校验升级计划结构、支持级别、证据和公开安全边界 |
| `/release-publish <version>` | 记录发布确认结果和最终公告位置 |
| `/usage-docs-generate <version>` | 根据已确认决策生成版本化产品手册并投影到 `mintlify/` |
| `/usage-docs-update <version>` | 更新当前版本手册或在授权下维护旧版本手册 |
| `/usage-docs-validate <version>` | 校验版本化产品手册、manifest、截图资产、Mintlify 导航和公开安全 |

本项目当前不引入草稿、待发布、已发布、撤回等复杂发布状态机。发布命令只记录计划、校验和确认事实。
