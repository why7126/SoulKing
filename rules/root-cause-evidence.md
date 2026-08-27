---
purpose: 证据化根因分析治理
content: 根因状态、证据链、人工补证、BUG 与返修门禁
created_at: 2026-08-21 22:50:52
updated_at: 2026-08-27 00:00:00
---

# 证据化根因分析治理

## 适用范围

本规则适用于问题排查、BUG 完善、BUG 来源 `/opsx-apply`、验收返修 `/opsx-modify`、效果不如预期探索和测试失败分析。

## 根因状态

| 状态 | 含义 | 允许动作 |
|---|---|---|
| `unknown` | 尚无足够证据定位根因 | 输出补证步骤，不确认根因 |
| `hypothesis` | 有假设但证据不足 | 说明假设、风险和验证方法 |
| `probable` | 多项证据指向同一原因，但仍缺闭环验证 | 可制定修复方案，但必须保留不确定性 |
| `confirmed` | 证据链闭环，能解释现象并被复现、日志、测试、截图或代码定位支持 | 可作为修复与验收依据 |

## 证据链要求

确认根因时 MUST 记录：

- 证据入口：仓库相对路径、测试名、日志摘要、截图编号、浏览器证据、API 请求摘要或用户补证来源。
- 证据类型：复现、日志、代码定位、配置差异、数据样本、截图、测试失败或回归测试。
- 根因结论：直接原因、触发条件、影响范围。
- 验证方式：修复前如何证明问题存在，修复后如何证明已闭环。

证据 MUST 脱敏；不得写入真实用户数据、密钥、访问令牌、Authorization header、Cookie、`.env` 内容、未脱敏日志、完整私有对象 URL 或本机绝对路径。

## 证据不足时的输出契约

证据不足时 MUST 输出人工补证步骤，至少包含：

- 需要补充的证据类型。
- 用户或测试人员可执行的采集步骤。
- 期望看到的关键字段、截图状态或日志摘要。
- 补证后如何更新 BUG、Change 或验收记录。

不得把 `unknown`、`hypothesis` 或 `probable` 包装成已确认根因。

## 命令接入

- `/explore`：只读分析时区分 confirmed、probable、hypothesis、unknown。
- `/bug-complete`：`root-cause.md` MUST 写入根因状态和证据链；证据不足则写补证步骤。
- `/bug-review`：默认 approve 或显式 approve 前 MUST 要求目标 BUG `root_cause_status: confirmed` 且 confirmed 证据链可定位；`unknown`、`hypothesis`、`probable`、缺少 `root-cause.md` 或缺少根因状态均为 approve blocker。
- `/opsx-apply`：BUG 来源实现前 SHOULD 复核根因状态；confirmed 缺证据时先补 BUG 文档或说明风险。
- `/opsx-modify`：验收返修若涉及“不如预期”或回归失败，先确认是根因证据不足、当前 Change 内偏差还是范围外新问题。
- Workflow Sync：扫描 `root-cause.md` 状态字段时，语义不明或 confirmed 无证据应报告 warning/blocker。

## 校验

轻量校验命令：

```bash
python scripts/validate-root-cause-evidence.py --all-active
```

聚焦校验：

```bash
python scripts/validate-root-cause-evidence.py --bug BUG-xxxx-slug
python scripts/validate-root-cause-evidence.py --change <change-id>
```

BUG review approve 门禁：

```bash
python scripts/validate-root-cause-evidence.py --bug BUG-xxxx-slug --require-confirmed
```
