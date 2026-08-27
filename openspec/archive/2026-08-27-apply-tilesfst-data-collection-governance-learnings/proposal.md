## 背景

TilesFST 的“产品数据采集与链路观测”治理把行为事件、请求日志、任务链路、流程节点、脱敏边界、保留周期和实现级校验串成一条可审计门禁。ProjectSoulKing 当前已有 API、DB、对象存储、媒体和治理脚本规则，但缺少面向音乐资产场景的统一数据采集规范，也缺少在 REQ、OpenSpec、Sprint 和归档阶段强制声明适用性或 N/A 原因的校验。

本 Change 应用 TilesFST 候选项 D1-D4，只吸收治理模式，不复制瓷砖业务语境，不实现业务采集功能。

## 变更内容

- 新增 SoulKing 版产品数据采集与链路观测标准，覆盖播放、下载、扫描导入、歌词、歌单、后台管理、认证、对象存储和媒体链路。
- 将采集规范门禁接入 `AGENTS.md`、相关 `rules/`、文档索引和命令顺序速查。
- 在 req、opsx、sprint 技能中加入采集声明检查，要求相关变更记录 `product_data_collection_observability`、适用层级、N/A 原因和验证摘要。
- 新增校验脚本和测试，用于检查标准文档、入口引用、技能门禁和目标 Change/REQ/Sprint/diff 的采集声明质量。
- 生成单份 `/spec-study` 学习报告，记录采纳、未采纳、验证和学习对象只读保护。

## 能力范围

### 新增能力

- `product-data-collection-observability-standard`：定义产品数据采集与链路观测治理标准，并要求触发范围内的研发流程声明适用性、验证结果和不适用原因。

### 修改能力

- `governance-workflow-tooling`：扩展 `/spec-study apply` 引入的数据采集治理门禁，使 Agent 命令和校验脚本能在相关变更中执行门禁检查。

## 影响

- API / DB：本 Change 不修改业务接口、Pydantic Schema、SQLAlchemy 模型或 SQLite schema；后续触发范围内的 Change 需同步或声明 N/A。
- 前台 Web / 后台管理端：本 Change 不修改 `app/static/`；后续行为事件、请求封装或日志审计展示变更需触发门禁。
- 对象存储 / 媒体：本 Change 不迁移对象或改存储实现；后续导入、播放、下载、封面、头像、歌词文件链路需声明采集适用性。
- Docker Compose / 桌面封装：不影响。
- 测试：新增治理脚本聚焦测试，不新增业务采集功能测试。
