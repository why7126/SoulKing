---
requirement_id: REQ-0002-single-tenant-trust-model
title: 单租户多账号信任模型
terminal: multi
version: v1
status: archived
owner: product
source: openspec/specs/single-tenant-trust-model/spec.md
priority: P1
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
parent_requirement:
related_spec: single-tenant-trust-model
---

# 单租户多账号信任模型

## 背景
ProjectSoulKing 当前已在代码与已生效 OpenSpec 中实现 `single-tenant-trust-model` 能力。为避免需求状态只存在于对话或规格结果中，本需求将该能力回填到 `issues/requirements`，作为可审计的历史需求档案。

## 目标用户
- 个人音乐库维护者
- 管理员
- 已登录普通用户（适用于面向前台或账号自助的能力）

## 用户价值
定义「单租户、多账号」安全与归属模型：同一部署实例使用**单一数据库连接**承载全部业务数据，曲库实体共享、歌单等按用户归属；应用层对业务 API 须会话鉴权，管理端点须管理员角色。传输加密、网络隔离、反向代理鉴权等若存在则属于部署环境，不在此承诺。

## 范围 In
- 覆盖 `single-tenant-trust-model` 已生效规格中的 5 个 Requirement。
- 以当前代码、OpenSpec 与产品文档描述的已实现行为为准。
- 保留规格中的 Notes 与 Known Gaps 作为后续演进输入。

## 范围 Out
- 不在本需求中新增接口、数据结构、权限边界或 UI 行为。
- 不直接修改 `openspec/specs/`，仅引用其作为已生效事实源。
- 不承诺修复 Known Gaps；后续若处理需另建 REQ/BUG 与 OpenSpec Change。

## 功能要求
- FR-001：单一数据存储连接
- FR-002：单租户多账号与共享曲库
- FR-003：管理端点须应用层授权
- FR-004：无应用层多租户分区语义
- FR-005：出站第三方密钥仅服务端使用

## UI 约束
- 涉及前台或后台壳的能力，遵守 `ui-design.md` 与 `rules/ui-design.md` 的既有要求。
- 非 UI 能力不新增界面约束，以对应 OpenSpec 说明为准。

## 关联需求
- 关联规格：`openspec/specs/single-tenant-trust-model/spec.md`
- 关联归档 Change：
- `2026-05-28-add-user-auth-system`

## Notes
- 产品为多账号场景：须登录后访问业务 API；种子管理员由环境变量在空库时创建。
- 服务端源码中**未**注册常见的跨域资源共享中间件；浏览器跨站访问时的限制主要来自浏览器同源策略，非应用内统一策略字段。
- 界面文案或脚本中可出现**环境变量名称**等提示语（例如提示需在服务端配置某变量），与「密钥取值写入前端」不是同一回事。
- 会话鉴权**不表示**请求必定成功：请求体验证错误、业务层未找到资源等仍会返回相应错误状态。

## Known Gaps
- **部署侧控制**：反向代理基本认证、IP 限制、TLS 终止等若启用，属运维与网关配置，本仓库应用代码无法逐项断言。
- **审计与追责**：按请求记录操作者身份的专用机制仍有限；事后归因依赖外部日志或部署扩展。

## 状态
- 当前状态：`archived`
- 归档原因：已实现能力的需求资产回填。
