## Context

`protect-admin-account` 已实现：API 拒绝禁用 `role=admin` 用户、启动时自愈种子 admin、后台 UI 对所有 admin 行隐藏禁用按钮。产品澄清后，保护对象应为**种子超级管理员**（`username` 与 `Settings.admin_username` 一致，默认 `admin`），而非所有管理员角色用户。

系统中可能存在多名 `role=admin` 的用户（如后续提升的普通管理员），这些账号应可被禁用；仅 `username=admin` 的账号作为系统种子超级管理员，不得被禁用。

## Goals / Non-Goals

**Goals:**

- 超级管理员判定统一为 `username` 匹配 `admin_username`（大小写不敏感），与 `seed_admin_user` 一致
- API 与 UI 仅保护超级管理员账号，其它 admin 角色用户恢复可禁用
- 规格与实现语义对齐，消除「角色级保护」的歧义

**Non-Goals:**

- 不改变「最后一名 admin 不可删除/降权」的现有逻辑（仍基于 `role=admin`）
- 不改变启动自愈逻辑（已基于 `admin_username`）
- 不新增超级管理员角色或权限体系
- 不禁止对超级管理员降权或软删除（除非后续单独要求）

## Decisions

### 1. 超级管理员判定：`username == admin_username`

**选择**：新增 `is_super_admin(user: User) -> bool`，比较 `user.username.lower() == settings.admin_username.lower()`。

**理由**：与 `seed_admin_user`、`get_user_by_username` 的配置源一致；支持 `.env` 自定义 `ADMIN_USERNAME`；语义明确区别于 `role=admin`。

**备选**：硬编码 `username == "admin"`。忽略配置，不推荐。

### 2. API 错误信息

**选择**：保留 `detail="不能禁用超级管理员账号"`（或沿用「不能禁用管理员账号」——与现有 UI 文案一致）。提案采用更精确的「不能禁用超级管理员账号」。

### 3. 后台 UI 判定方式

**选择**：在 `AdminUserOut` 增加 `is_super_admin: bool` 字段，由服务端 `is_super_admin(user)` 计算；前端用 `u.is_super_admin` 决定是否渲染禁用按钮。

**理由**：前端无需硬编码 `admin` 或额外请求配置；与 `ADMIN_USERNAME` 变更保持同步。

**备选**：前端 `u.username.toLowerCase() === 'admin'`。简单但与配置脱节。

### 4. 回退过宽保护

**选择**：直接修改现有 `role=admin` 判断为 `is_super_admin(user)`，不保留双重条件。

## Risks / Trade-offs

- **[超级管理员被降权后禁用]** 若先将 `admin` 用户降为 `user` 再禁用，保护失效 → 可接受；降权本身已是敏感操作，且「最后一名 admin」仍有保护
- **[ADMIN_USERNAME 与库中 username 不一致]** 配置变更后旧种子账号失去保护 → 运维文档说明；判定始终读当前配置
- **[is_super_admin 字段暴露]** 列表 API 增加布尔字段 → 信息无害，便于 UI

## Migration Plan

1. 部署代码变更（无数据库迁移）
2. 验证：`admin` 用户不可禁用；其它 `role=admin` 用户可禁用
3. 合并 spec delta 并归档本变更及清理重复的 `protect-admin-account` 活跃目录（若仍存在）

## Open Questions

（无）
