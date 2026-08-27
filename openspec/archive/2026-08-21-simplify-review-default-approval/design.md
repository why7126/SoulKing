---
purpose: OpenSpec Change 设计说明
content: REQ/BUG review 命令默认通过语义的治理设计
created_at: 2026-08-21 13:46:22
updated_at: 2026-08-21 13:55:03
---

# 设计说明

## 背景

REQ 和 BUG 评审的常规路径是通过后进入 Sprint，再转 OpenSpec Change。当前要求显式输入 `--approve`，而多数评审通过并不需要额外分支信息，导致命令推荐和人工执行重复。

## 方案

- 无 flag 的 `/req-review <REQ-full-id>` 与 `/bug-review <BUG-full-id>` 统一解释为 `approve`。
- 非通过分支继续使用显式 flag，避免误把拒绝、延后或不修复当作默认动作。
- 目录迁移、Workflow Sync、AI Usage hook 和下一步命令沿用原批准路径，只调整触发条件和推荐文案。

## 兼容性

- 常规推荐入口省略批准 flag。
- 若历史会话或外部提示仍携带 `--approve`，应按默认批准语义等价处理；后续文档不继续生成该写法。

## 风险与取舍

- 收益：减少高频常规通过路径输入成本。
- 风险：用户误触无 flag 命令时会直接通过，因此拒绝、延后和不修复必须显式表达。
- 取舍：保留非通过 flag 的强显式性，避免降低评审门禁本身的审慎程度。
