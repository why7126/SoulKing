---
purpose: 测试规范
content: 后端、前端调试、OpenSpec、最小相关验证和手工验证要求
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-27 01:00:00
---

# 测试规范

常用验证：

```bash
python scripts/validate-directory-structure.py
python scripts/validate-generated-docs.py --strict
python -m pytest
npm run test:e2e
```

如果项目尚未具备完整 pytest 用例，应至少运行与变更相关的脚本、API 手工验证或浏览器验证，并在回复中说明覆盖范围。

验证选择遵守最小相关原则：根据变更影响面选择最能暴露回归的命令或手工检查，不因一次小改默认运行全量套件，也不得用无关绿灯替代相关证据。涉及治理文档或脚本时优先运行对应 `validate-*` 脚本；涉及 API、DB、UI、部署、安全或对象存储时补充对应专项验证。

BUG 修复、验收返修和测试失败分析 SHOULD 回扣 `rules/root-cause-evidence.md`。当根因状态为 `confirmed` 时，测试证据可以作为证据链之一，但必须能定位到测试名、失败/通过摘要和对应行为；状态为 `unknown`、`hypothesis` 或 `probable` 时，测试计划应说明仍需补充的复现、日志、截图或回归证据。

最终回复和 Change 记录必须说明已运行验证与影响面的对应关系；未运行的高相关验证必须说明原因。

## 产品数据采集与链路观测测试门禁

涉及 API、DB、日志审计、行为事件、播放/下载、媒体导入、Task Trace、前台请求封装、后台请求封装或对象存储观测的变更，必须读取 `docs/standards/product-data-collection-observability.md`，并补充或声明 `product_data_collection_observability`、`affected_layers`、N/A 原因与验证摘要。

相关验证应覆盖行为事件、请求日志、直接 API、Task Trace、脱敏、保留周期、旧数据兼容、播放/下载、对象存储和端侧链路 ID 透传中的适用项。相关 Change 应运行 `python scripts/validate-product-data-observability-gates.py --change <change-id>` 或等价聚焦校验。
