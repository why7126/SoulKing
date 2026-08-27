## Context

前台（`index.html` + `studio.css` + `frontend.js`）与后台（`admin.html` + `admin-studio.css` + `admin.js`）均在侧栏底部提供用户头像触发的向上弹出菜单。菜单定位、收起态弹出规则已由 `sidebar-user-menu-popout` 与多轮变更对齐；但「退出登录」项仍存在实现漂移：

- 后台通过 `.adm-user-menu-item:last-child` 施加 `--adm-danger` 色，前台无对应样式（虽已定义 `--sk-danger`）。
- 前台菜单含四项，后台仅「返回前台」「退出登录」两项，均无「退出」前的视觉分组。
- 两边点击退出均直接 `showToast`，无确认步骤；而后台删除等危险操作使用确认 overlay。

约束：不修改菜单 HTML 的 `role="menu"` 语义、不改变 `sidebar-user-menu-popout` 的定位契约；本变更仅涉及菜单项 markup/class、样式与退出 handler。真实认证 API 仍不在范围内。

## Goals / Non-Goals

**Goals:**

- 前后台「退出登录」使用统一的显式危险样式（class + 设计 token），不依赖 DOM 顺序。
- 「退出登录」与上一菜单项之间具备可见分隔，强化「会话结束」与导航/账户项的层次。
- 激活「退出登录」时先关菜单，再通过既有 `#modalOverlay` / `openModal` 二次确认；确认后与现网一致的演示 toast。
- 在 `web-static-client-shells` 中写清验收场景，防止再次只改一侧 CSS。

**Non-Goals:**

- 接入真实登出 API、清除 session/cookie、跳转登录页。
- 修改个人资料、修改密码、进入后台、返回前台的行为（除菜单关闭时序外）。
- 改动 `sidebar-user-menu-popout` 的收起态定位或 z-index。
- 统一表格「更多」菜单的 `danger-text` 命名（可后续 refactor，本变更仅用户菜单）。

## Decisions

### 1. 危险样式：显式 class `user-menu-item--destructive`

**选择**：在前后台退出按钮上增加共享 class 名 `user-menu-item--destructive`（与各壳原有 `sk-user-menu-item` / `adm-user-menu-item` 并存）。CSS 在各壳文件中分别映射到 `--sk-danger` / `--adm-danger` 与相同 hover 背景 `rgba(248, 113, 113, 0.1)`。

**理由**：避免 `:last-child` 在增删菜单项时误着色；与探索阶段结论一致。

**备选**：继续 `:last-child` — 已拒绝，脆弱且前后台仍可能分叉。

### 2. 分组：退出项 `border-top` + 上内边距

**选择**：对 `.user-menu-item--destructive`（或包裹层）使用 `margin-top: 4px`、`padding-top` 略增，并在项上方绘制 `1px solid` 分隔线（使用各壳 `--sk-border` / `--adm-border`）。不新增独立 `<hr>` 节点，减少 DOM 与可访问性噪音。

**理由**：纯 CSS、与现有 panel 边框 token 一致；前台四项、后台两项均适用。

**备选**：插入 `<div role="separator">` — 可行但需额外 aria；本阶段优先 CSS 分隔。

### 3. 确认交互：复用 `openModal`

**选择**：提取或内联共享流程 `confirmLogout()`（各脚本一份，逻辑对称）：

1. 关闭用户菜单（`setFrontUserMenuOpen(false)` / `setAdminUserMenuOpen(false)`）。
2. `await openModal({ title: "退出登录", message: "确定要退出当前账号吗？", confirmText: "退出", cancelText: "取消" })`。
3. 若结果为确认（与现有 `closeModal(true)` 约定一致），`showToast("已退出（演示：刷新页面可重新进入）", "info")`。
4. 若取消或关闭，无 toast。

**理由**：前后台均有 `#modalOverlay` 与 `openModal`；与删除确认模式一致，无需新建 overlay。

**备选**：后台专用 `#deleteOverlay` — 文案为「确认删除」，语义不符。

### 4. 前台菜单项点击时序

**选择**：退出项仍经 `handleFrontUserMenuItem` 包裹，在 resolver 内调用 `confirmLogout()`，保留 350ms pointer-events 防抖，避免菜单闪退竞态。

**理由**：与 `fix-front-user-menu-dismiss` 既有修复兼容。

### 5. 后台移除 `:last-child` 规则

**选择**：删除 `admin-studio.css` 中 `.adm-user-menu-item:last-child` 及 `:hover` 规则，改由 `.user-menu-item--destructive` 承担。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 确认框多一步操作，演示环境略繁琐 | 与删除等危险操作一致；真实登出时合理 |
| `openModal` 返回值约定与个别调用不一致 | 实现时对齐现有 `closeModal(true/false/null)` 判断方式 |
| 分隔线 + 危险色在收起态窄菜单中拥挤 | 沿用 `min-width: 160px` 与 `white-space: nowrap`；手动验收收起态 |
| 未来接入 API 时需改 confirm 分支 | spec 注明确认后执行「登出副作用」扩展点，toast 为当前占位 |

## Migration Plan

1. 先改 HTML class 与 CSS，再改 JS handler，便于分步目视对比。
2. 无数据迁移；部署静态资源即可。
3. 回滚：还原四个静态文件与 spec delta。

## Open Questions

（无 — 用户已确认「颜色 + 分组 + 确认交互」均需对齐。）
