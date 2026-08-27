## Context

`user-administration` 规格已定义 `PATCH /admin/users/{id}` 可修改昵称、角色、`is_active`。实现函数 `update_admin_user` 逻辑完整（含超级管理员保护、禁用时踢会话），但在重构 `admin_user_out()` 时 `@router.patch` 装饰器被误删，函数成为未挂载的普通函数。

当前路由表（同路径 `/admin/users/{user_id}`）：

```
DELETE  /admin/users/{user_id}           ✓ 已注册
PATCH   /admin/users/{user_id}           ✗ 未注册 → 405
POST    /admin/users/{user_id}/reset-password  ✓
```

## Goals / Non-Goals

**Goals:**

- 恢复 PATCH 路由，使禁用/启用/改角色恢复正常
- 验证通过 HTTP 层（非仅 Python 直调）确认修复

**Non-Goals:**

- 不改变 `update_admin_user` 业务逻辑
- 不修改前端 `admin.js` 请求方式
- 不涉及其它 API 路由

## Decisions

### 1. 修复方式：补回装饰器

**选择**：在 `update_admin_user` 前添加 `@router.patch("/admin/users/{user_id}", response_model=AdminUserOut)`。

**理由**：最小 diff，恢复既有设计；函数体无需改动。

### 2. 验证策略：HTTP 集成测试

**选择**：使用 `TestClient` 或等价方式发送 `PATCH /admin/users/{id}`，断言非 405。

**理由**：上次验证直调 `update_admin_user()` 通过了，但 HTTP 层仍 broken；须覆盖路由注册。

### 3. 预防：规格回归场景

**选择**：在 spec delta 增加「PATCH 端点 HTTP 可达」场景。

**理由**：文档化该回归点，归档后成为正式验收标准。

## Risks / Trade-offs

- **[无]** 单行修复，风险极低
- **[遗漏其它路由]** 本次仅 PATCH；可顺带 grep 确认其它 `@router.*` 装饰器完整 → 实现任务中快速检查

## Migration Plan

1. 补装饰器 → 重启服务
2. 后台用户管理：禁用 test 用户 → 确认 200 且状态更新
3. 归档 change

## Open Questions

（无）
