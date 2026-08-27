---
title: 产品版本发布目录
purpose: 说明产品版本发布对象、Mintlify 公告源文件和发布校验材料的目录边界
created_at: 2026-07-02 14:56:58
updated_at: 2026-07-02 14:56:58
owner: product
status: draft
---

# 产品版本发布目录

`releases/` 用于承载对外产品版本发布材料。一个产品版本可以合并多个 Sprint，并追踪关联 REQ、BUG 和 OpenSpec Change。

## 目录结构

```text
releases/
├── README.md
├── mint.json
├── templates/
│   ├── release.json
│   └── announcement.mdx
└── vX.Y.Z/
    ├── release.json
    └── announcement.mdx
```

## 文件职责

| 文件 | 职责 |
|---|---|
| `release.json` | 机器可读产品发布对象，记录版本、范围、门禁、影响、升级与回滚 |
| `announcement.mdx` | Mintlify 公开公告源文件 |
| `mint.json` | Mintlify 静态文档配置 |

## 发布门禁

发布前必须校验：

- OpenSpec Change 已 archive。
- 测试按范围执行并记录。
- API 变更已同步 FastAPI OpenAPI 与前端调用；ProjectSoulKing 未启用 Orval 时记录为 `na`。
- Docker Compose 与部署文档已同步。
- 数据库迁移、数据库文档和回滚说明已同步。
- `.env.example` 与相邻注释已同步。
- `PRODUCT_VERSION`（如启用）与发布对象版本一致，或记录不更新原因。
- Mintlify build / preview 或等价校验通过。

## 边界

- 不替代 `iterations/` Sprint 四件套。
- 不替代 `issues/` 需求与 BUG 文档。
- 不替代 `openspec/changes/` 或 `openspec/specs/`。
- 不存放运行时生成站点、真实客户数据、密钥、数据库连接串或不可公开运维信息。
