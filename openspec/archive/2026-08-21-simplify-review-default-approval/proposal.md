---
purpose: OpenSpec Change 提案
content: 简化 REQ/BUG review 命令默认通过语义
created_at: 2026-08-21 13:46:22
updated_at: 2026-08-21 13:46:22
---

## 为什么

`/req-review` 和 `/bug-review` 是进入 Sprint 与 OpenSpec 的高频门禁命令。当前规范要求常规通过场景反复输入 `--approve`，而拒绝、延后、不修复才是真正需要额外表达的分支，导致下一步提示和人工执行都偏繁琐。

## 变更内容

- 将 `/req-review <REQ-full-id>` 与 `/bug-review <BUG-full-id>` 的无 flag 行为定义为默认 `approve`。
- 保留 `--reject`、`--defer`、`--wont-fix` 作为显式非通过分支；`--wont-fix` 仅适用于 BUG。
- 同步命令顺序、需求/BUG 管理规则和下一步示例，避免继续推荐常规通过时携带 `--approve`。

## 影响范围

- 影响范围：Agent 命令技能、治理规则、命令顺序文档和治理日志。
- 不影响：业务 API、数据库、前台 Web、后台管理端、对象存储、Docker、桌面封装。
