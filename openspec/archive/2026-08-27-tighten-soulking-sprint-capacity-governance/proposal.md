---
purpose: OpenSpec Change proposal
content: 收紧 SoulKing Sprint 容量配置、超出策略和容量门禁验证
created_at: 2026-08-27 08:54:38
updated_at: 2026-08-27 08:54:38
---

# 收紧 SoulKing Sprint 容量治理

## 为什么

`sprint-001` 的机器事实源显示容量为 3 人天、正式范围估算为 9.5 人天，容量占用已经超过 300%。现有规则和技能虽提到超过 120% 时应引导拆分，但缺少完整的三段式容量策略、`sprint.yaml` 字段模板、OpenSpec 规格和聚焦测试，容易让超载 Sprint 继续追加范围或让 `sprint.md` 与机器事实源漂移。

本 Change 应用 ProjectTilesFST 的 Sprint 容量配置和超出策略学习项 A1-A5，并按 ProjectSoulKing 的个人音乐资产管理项目边界改写。

## 变更内容

- 在 `governance-workflow-tooling` 能力中增加 Sprint 容量门禁规则。
- 更新 Sprint 生命周期规则和 `/sprint-propose` 技能，明确 `<=100%`、`100%~120%`、`>120%` 三段处理策略。
- 强化 `sprint.yaml` 容量字段模板，要求记录 `capacity_person_days`、`capacity_usage`、`fix_buffer_person_days`、`fix_buffer_ratio` 和 `capacity_gate`。
- 更新 `scripts/add-sprint-scope-item.py`，追加范围时同步刷新容量占用、fix buffer 和 capacity gate 结果。
- 新增聚焦测试，确保规则、技能、OpenSpec 规格和脚本容量计算保持一致。
- 生成单份 `/spec-study` 学习报告，记录采纳、未采纳、验证和只读保护结论。

## 影响范围

- API：无影响。
- 数据库：无影响。
- 前台 Web / 后台管理端：无影响。
- 对象存储：无影响。
- Docker Compose：无影响。
- 测试：新增治理脚本聚焦测试。
- 业务运行时代码：不修改 `app/`、`app/static/`、`packaging/`。
