## 1. OpenSpec 与标准文档

- [x] 1.1 创建 `product-data-collection-observability-standard` delta spec，定义 SoulKing 数据采集和链路观测治理能力。
- [x] 1.2 新增 `docs/standards/product-data-collection-observability.md`，覆盖音乐资产场景、四层模型、脱敏、保留周期和接入清单。
- [x] 1.3 更新文档索引，保持详细事实源单一归属。

## 2. 入口、规则与技能门禁

- [x] 2.1 更新 `AGENTS.md` 和命令顺序速查，接入数据采集门禁触发范围和完成检查。
- [x] 2.2 更新 API、数据库、测试、数据管理、需求管理和 Sprint 规则，声明必读、必声明、N/A 原因和验证要求。
- [x] 2.3 更新 req、opsx、sprint 技能，加入数据采集与链路观测声明检查。

## 3. 校验脚本与测试

- [x] 3.1 新增标准文档完整性校验脚本。
- [x] 3.2 新增门禁校验脚本，支持 Change、REQ、Sprint 和 diff 聚焦检查。
- [x] 3.3 新增聚焦测试，覆盖标准缺失、入口缺失、声明缺失和 N/A 原因质量。

## 4. 学习报告、同步与验证

- [x] 4.1 生成单份 `docs/spec-logs/YYYYMMDDhhmmss-study-tilesfst-data-collection.md` 学习报告。
- [x] 4.2 复核学习对象只读、本项目未修改业务运行时代码。
- [x] 4.3 运行脚本编译、聚焦测试、采集门禁、OpenSpec、目录结构、文档卫生和 Sprint scope 校验。
- [x] 4.4 运行 Workflow Sync 和 AI Usage post-command hook。
