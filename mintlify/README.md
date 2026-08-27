---
created_at: 2026-08-04 00:00:00
updated_at: 2026-08-04 00:00:00
purpose: Mintlify 公开产品手册源目录说明
---

# Mintlify 文档站源目录

`mintlify/` 承载 ProjectSoulKing 公开产品手册站源文件、Mintlify `docs.json` 配置、公告投影和可公开截图资产。

- `releases/vX.Y.Z/usage-docs/` 是版本产品使用文档事实源和发布快照。
- `mintlify/docs/vX.Y.Z/` 由 release 快照同步或投影生成。
- `mintlify/docs/latest/` 指向最新已发布且 usage docs 站点校验通过的版本。
- `mintlify/releases/vX.Y.Z/announcement.mdx` 由版本发布公告投影生成。
- `mintlify/assets/screenshots/` 集中存放按内容 hash 命名的共享截图资产。
- `mintlify/docs.json` 是 Mintlify 主配置；不得再维护 `mintlify/mint.json`。

发布前运行：

```bash
python scripts/validate-usage-docs.py --release-dir releases/<version>
python scripts/validate-mintlify-site.py
```

本目录不得存放构建产物、真实用户数据、密钥、数据库连接串、真实 `.env`、Authorization header、Cookie、运行时数据库或不可公开运维信息。
