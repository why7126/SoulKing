---
purpose: 目录结构规范
content: ProjectSoulKing 目录职责、禁止事项和新增文件边界
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 目录结构规范

| 路径 | 职责 |
|---|---|
| `app/` | FastAPI 后端、SQLAlchemy 模型、对象存储、认证和静态 Web 客户端 |
| `app/static/` | 前台、后台、登录页 HTML/CSS/JS 与视觉资产 |
| `openspec/` | OpenSpec 项目说明、活跃变更、归档变更和已生效规格 |
| `openspec/changes/` | 活跃 OpenSpec Change；不得在此目录下建立 `archive/` |
| `openspec/archive/` | 已归档 OpenSpec Change，目录名格式为 `YYYY-MM-DD-<change-id>` |
| `issues/` | 需求和 BUG 生命周期文档 |
| `iterations/` | Sprint 计划、执行、验收和复盘 |
| `docs/` | 长期产品与技术文档 |
| `docs/standards/` | API、测试、认证、文件上传、原型驱动 UI 验收等长期标准 |
| `rules/` | AI 和工程强制规则 |
| `scripts/` | 迁移、验证、工作流同步和调试脚本 |
| `deploy/` | 本地、生产和产品手册站部署矩阵；只允许 README、环境化 Compose、env 示例和部署脚本，真实 env 禁止提交 |
| `packaging/` | macOS 等本地封装辅助 |
| `data/` | 本地运行数据库和调试数据，禁止提交真实运行时文件 |
| `import/` | 本地待导入媒体目录，禁止提交个人媒体 |
| `.agents/` | Agent 技能入口，技能位于 `.agents/skills/<command-name>/SKILL.md`；当前包含 `/explore`、需求/缺陷/Sprint/OpenSpec、`/spec-opt`、`/spec-study`、发布、镜像、升级和产品手册命令 |
| `releases/` | 产品版本发布计划、公告模板和发布证据；历史版本按 `releases/<version>/` 存放 |
| `mintlify/` | 公开产品手册站源目录，使用 `docs.json` 作为 Mintlify 主配置；版本页面由 `releases/<version>/usage-docs/` 投影生成 |
| `docs/spec-logs/` | 规范工程日志；`CHANGELOG.md` 为累计变更历史索引，`/spec-study` 学习报告使用 `YYYYMMDDhhmmss-study-xxx.md`，`/spec-opt` 治理迭代日志使用 `YYYYMMDDhhmmss-governance-xxx.md` |

新增顶层目录需先说明职责，并在必要时同步本文档、`project.yaml` 和目录校验脚本。当前业务代码保留在 `app/`；迁移到 `src/` 应作为独立重构处理。

## 本地 env 文件

允许本地存在被 `.gitignore` 覆盖且不被 Git 跟踪的真实 env 文件：`.env`、`.env.*`、`deploy/local/*.env`、`deploy/prod/*.env`、`scripts/build-images.env`。这些文件用于本地运行、部署或镜像构建，其存在不作为目录结构、OpenSpec 归档或 Sprint 归档阻断。

真实 env 文件不得提交，不得复制进 `releases/`、`mintlify/`、`openspec/archive/`、`issues/`、`iterations/` 或 AI Usage 产物，不得在命令输出、验证证据或回复中展开内容。环境变量变更需要同步的是 `.env.example`、`deploy/**/*.env.example` 或 `scripts/build-images.env.example` 等示例文件。

## deploy 部署矩阵边界

`deploy/` 用于承载本地和生产部署环境矩阵，不是运行时数据目录，也不是云资源管理目录。

- `deploy/local/` 表达本地开发环境矩阵，`deploy/prod/` 表达生产或生产等价部署矩阵。
- `deploy/scripts/` 承载环境解析、启动、停止和配置校验逻辑；根 `scripts/docker-up.sh` 与 `scripts/docker-down.sh` 仅作为兼容 wrapper。
- `deploy/` MUST NOT 提交真实 `.env`、真实密钥、真实数据库连接串、对象存储凭据、真实用户数据、运行时数据库文件、MinIO 对象数据、镜像 tar 包或离线交付包。
- 真实 `deploy/**/*.env` 可作为本地/生产运行配置存在于工作区，但必须保持 Git ignored / untracked；目录结构和归档门禁只阻塞已跟踪、待提交或内容泄漏的真实 env。

## Mintlify 公开站点边界

`mintlify/` 是公开产品手册站源目录和投影目录，不是 release 事实源。

- `mintlify/docs.json` 是唯一主配置；不得恢复 `mintlify/mint.json`。
- `mintlify/` 只允许公开页面、导航配置、公告投影、站点 manifest 和共享截图资产。
- `mintlify/` MUST NOT 存放 `.env`、真实用户数据、密钥、数据库连接串、Authorization header、Cookie、生产私有域名、运行时数据库、日志、构建产物、依赖目录、`.mintlify/`、`dist/`、`build/`、`.next/` 或 coverage。
- `mintlify/` 不得替代 `releases/<version>/release.json`、`releases/<version>/usage-docs/manifest.json`、`docs/`、`issues/`、`iterations/` 或 `openspec/`。

## 规范工程日志

规范工程日志统一放入 `docs/spec-logs/`。`docs/spec-logs/CHANGELOG.md` 是规范工程累计变更历史索引；每次规范、脚本、命令、目录边界或校验规则更新后，应追加摘要并链接同目录详细日志或学习报告。

该目录不替代 `docs/standards/`、`docs/knowledge-base/`、`openspec/changes/` 或 `iterations/`，且不得包含用户隐私数据、真实客户数据、密钥、访问令牌、本机绝对路径、未脱敏日志、聊天原文、工单原文、截图中的个人信息或学习对象源码。

## Git 安全检查

推送或交付前 SHOULD 运行 `/git-check` 或 `python scripts/git-check.py`。该检查只扫描 staged/tracked 文件，不读取 ignored 且未被跟踪的真实 env 内容；发现真实 env、运行时数据、密钥、本机路径、大文件或私有数据时必须先处理。

## 文档治理检查

治理文档、规范工程日志、Agent 入口或长期标准更新后 SHOULD 运行 `python scripts/validate-doc-governance.py`。该检查只读扫描 Markdown frontmatter、脚手架残留、spec-log 隐私路径和核心文档预算，不自动修改文件。
