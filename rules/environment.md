---
purpose: 环境规范
content: 本地、Docker、ProjectMinio 和环境变量约束
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 环境规范

- 本仓库 `docker-compose.yml` 只启动 app。
- 对象存储由并列 `../ProjectMinio` 提供。
- Docker 内数据库路径使用 `/data/music.db`，宿主机映射到 `./data/`。
- 本机直跑时需确保 SQLite 路径和 MinIO endpoint 指向本机可访问地址。
- 真实本地 env 文件允许存在于 `.env`、`.env.*`、`deploy/local/*.env`、`deploy/prod/*.env`、`scripts/build-images.env`，前提是被 `.gitignore` 覆盖且不被 Git 跟踪；这些文件的存在不阻断归档或目录校验。
- 环境变量契约变更必须同步 `.env.example`、`deploy/**/*.env.example` 或 `scripts/build-images.env.example`；不得把真实 env 内容写入 release、Mintlify、归档证据、AI Usage 或公开日志。

## 版本升级 env diff

版本部署升级计划 MUST 使用 env diff 识别来源版本和目标版本之间的环境变量差异。env diff 默认覆盖：

```text
.env.example
deploy/**/*.env.example
scripts/build-images.env.example
```

输出分类 MUST 至少包含：

| 分类 | 含义 |
|---|---|
| `added` | 目标版本新增变量。 |
| `removed` | 目标版本删除变量。 |
| `changed_default` | 示例默认值变化。 |
| `required_in_production` | 生产必须显式配置。 |
| `unsafe_example_value` | 生产不得使用示例值。 |
| `manual_review` | 无法自动判断，需要人工复核。 |

env diff 输出只能包含变量名、示例文件路径、分类、说明和修复建议；不得输出真实生产 `.env` 值。历史版本没有 env 示例快照时，跨版本计划 MUST 标记 `manual_review`，不得伪造完整 diff。
