## Why

`optimize-front-layout-nav` 将前台用户菜单置于侧栏底部后，用户反馈菜单「一闪而过」、无法持续操作。排查表明问题主要来自 **打开与关闭路径的事件时序竞态**（document 级 outside-click 与菜单项 handler 在打开后的同一激活周期内误关菜单），而非单纯 DOM 位置或 overflow 裁切。

曾将用户区临时移至顶栏右上角做对照实验，闪退仍复现，说明根因在 JS 交互而非侧栏布局。用户区已移回侧栏底部，并与后台壳对齐为「头像按钮 + 用户名」结构（`#frontUserMenuBtn.sk-user-avatar`）。

本变更在保持侧栏底部布局的前提下，修复菜单展开后立即关闭的问题，使菜单保持可见直至用户选择菜单项或点击外部。

## What Changes

- **交互时序防护（`frontend.js`）**
  - 打开菜单后设置 `frontUserMenuInteractAfter`（350ms）冷却，`handleFrontUserMenuItem` 在冷却期内忽略误触关闭。
  - 打开后短暂禁用菜单 `pointer-events`，经双 `requestAnimationFrame` 再恢复，避免同帧内菜单项被误点。
  - 触发器 `click` 保留 `stopPropagation()`；document `click` 在菜单已展开且点击不在 `#frontUserMenu` / `#frontUserMenuBtn` 内时关闭。
- **布局与样式（`index.html` + `studio.css`）**
  - 用户区位于 `.sk-sidebar-bottom`：上方曲库统计（「X 首歌库」），下方 `.sk-user-row`（头像按钮 + 用户名）；菜单向上弹出。
  - 顶栏 **不** 再包含用户菜单或头像触发器。
  - `.sk-sidebar-bottom` 使用 `position: relative`；`.sk-user-menu` 使用 `bottom: calc(100% + 6px)` 向上展开（与后台 `adm-user-menu` 一致）。
- **保持现有菜单项行为**：个人资料 / 修改密码 / 退出登录为 toast 占位；「进入后台」整页跳转 `/admin`；选择菜单项后关闭。
- 递增 `frontend.js`、`studio.css`（及 `index.html` 引用）的 `?v=` 缓存版本。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：强化「前台壳侧栏底部用户菜单」— 触发控件为侧栏底部头像按钮；菜单展开后 MUST 保持可见，MUST NOT 因与打开同一次用户激活相关的关闭逻辑而立即消失；顶栏不含用户菜单入口。

## Impact

- **前端**：`app/static/frontend.js`（`setFrontUserMenuOpen`、`handleFrontUserMenuItem`、`initFrontUserMenu`、document outside-click）；`app/static/index.html`（侧栏底部 DOM）；`app/static/studio.css`（用户区与菜单定位）。
- **后端 / API**：无变更。

## Investigation Notes

| 尝试 | 结果 |
|------|------|
| `ignoreNextOutsideClick` + `closest(".sk-sidebar-bottom")` | 部分环境仍闪退，已替换为当前方案 |
| Popover API / body portal | 曾试验，未作为最终方案 |
| 用户区移至顶栏 | 闪退仍复现，排除「仅侧栏 overflow」为唯一根因 |
| 移回侧栏底部 + admin 对齐结构 + 350ms 防护 | **当前实现** |
