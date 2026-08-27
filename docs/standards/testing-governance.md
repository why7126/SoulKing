---
purpose: 测试治理标准
content: 变更验证、回归范围、最小相关证据和记录要求
created_at: 2026-07-15 00:00:00
updated_at: 2026-08-21 22:50:52
---

# 测试治理标准

每个 OpenSpec Change 的 `tasks.md` 应记录实际运行的验证命令。无法运行自动化测试时，必须说明原因，并给出手工 API 或浏览器验证结果。

## 最小相关证据

验证命令应覆盖本次变更真实触达的面：

- 仅修改 Markdown 治理资产时，运行文档、语言、目录或上下文预算校验。
- 修改治理脚本时，运行被修改脚本本身，并补充相关规则校验。
- 修改 API、认证、数据库、对象存储或部署时，运行对应专项测试、脚本或 smoke 验证。
- 修改 UI 时，运行相关浏览器或手工验收，并记录视口、入口和关键状态。

验证记录必须说清楚每条命令验证了什么风险；不能只罗列命令。

## 根因证据

BUG 修复、验收返修和测试失败分析 SHOULD 遵守 `../../rules/root-cause-evidence.md`。触达 BUG 根因或返修证据时，优先运行聚焦校验：

```bash
python scripts/validate-root-cause-evidence.py --bug <BUG-id>
python scripts/validate-root-cause-evidence.py --change <change-id>
```
