## Context

### 当前 DOM 结构（`index.html`）

```
.sk-sidebar-bottom (position: relative)
├── .sk-sidebar-stat-row          ← 曲库统计（非菜单触发器）
│   ├── #sidebarSongCount
│   └── 「首歌库」
├── .sk-user-row
│   ├── button#frontUserMenuBtn.sk-user-avatar   ← 唯一触发器
│   └── .sk-user-meta > strong（SoulKing）
└── #frontUserMenu.sk-user-menu (absolute, 向上弹出)
```

顶栏 `.studio-header-end` 仅保留歌单相关操作按钮，**不含**用户头像或菜单。

结构与后台壳对齐：

```
.adm-sidebar-bottom → .adm-user-row → #adminUserAvatarBtn + .adm-user-meta → #adminUserMenu
```

### 当前脚本行为（`frontend.js`）

| 路径 | 行为 |
|------|------|
| `#frontUserMenuBtn` click | `stopPropagation()` + toggle `hidden` |
| `setFrontUserMenuOpen(true)` | 设 `frontUserMenuInteractAfter = now + 350`；菜单 `pointer-events: none` → 双 rAF 后恢复 |
| `handleFrontUserMenuItem(action)` | 菜单 hidden 或冷却期内 return；否则关闭并执行 action |
| document click | 菜单已展开且 target 不在 menu/btn 内 → 关闭 |

### 问题背景

`optimize-front-layout-nav` 曾将触发器改为整行 `button.sk-user-trigger`，用户报告菜单闪退。调试日志显示关闭常来自菜单项 handler 或 outside-click 在打开后同一事件循环内触发，而非用户主动点击外部。

将用户区临时移至顶栏后问题依旧，确认需从 JS 时序入手而非仅调整 CSS 层叠。

## Goals / Non-Goals

**Goals:**

- 单击侧栏底部头像按钮后菜单稳定展开，可点击四项菜单项
- 点击菜单与触发按钮外区域关闭菜单
- 选择菜单项后关闭（行为不变）
- 用户区固定在侧栏底部，顶栏无重复入口
- 视觉与交互模式与后台侧栏底部用户区一致

**Non-Goals:**

- 重写为 Popover API / React 组件
- 修改菜单项文案或认证 API
- 改动后台 `admin.js` 用户菜单（本变更仅对齐前台 DOM/CSS 模式）
- 使「首歌库」统计行可点击展开菜单（统计与用户区职责分离）

## Decisions

### 1. 350ms 交互冷却 + `pointer-events` 延迟（替代 `ignoreNextOutsideClick`）

**选择**：打开时记录 `frontUserMenuInteractAfter`；`handleFrontUserMenuItem` 在冷却结束前不关闭菜单。打开后短暂 `pointer-events: none`，双 `requestAnimationFrame` 后恢复。

**理由**：调试表明闪退常由菜单项 listener 在打开后立即执行 `closeFrontUserMenu` 引起；冷却窗口比单次 document 标志更可靠地覆盖菜单项误触。`pointer-events` 延迟避免同帧 hit-test 落在刚展开的菜单项上。

**备选（已弃用）**：`frontUserMenuIgnoreOutsideClick` + `closest(".sk-sidebar-bottom")` —— 仍有个别路径在标志消费前关闭；document 判定改为精确的 menu/btn `contains` 即可。

### 2. 触发器为头像按钮，非整行 button

**选择**：`#frontUserMenuBtn` 为 `.sk-user-avatar` 圆形按钮；用户名在相邻 `.sk-user-meta` 内，不可点击。

**理由**：与 `admin.html` 一致，减少整行 button 带来的 hit area / 事件冒泡边界问题；用户明确将用户区移回侧栏底部并对齐后台。

### 3. 菜单定位于侧栏底部容器内、向上展开

**选择**：`.sk-user-menu { left: 6px; right: 6px; bottom: calc(100% + 6px); z-index: 30 }`；`.sk-sidebar-bottom { position: relative }`。

**理由**：与后台 `adm-user-menu` 一致；菜单在侧栏底部上方弹出，不占用顶栏空间。

### 4. document outside-click 使用 menu/btn `contains`

**选择**：`!els.frontUserMenu.contains(e.target) && !els.frontUserMenuBtn.contains(e.target)` 时关闭。

**理由**：触发器仅为头像按钮，无需将整个 `.sk-sidebar-bottom`（含统计行）视为安全区；统计行点击应能关闭已展开菜单。

### 5. 触发器保留 `stopPropagation`

**选择**：头像按钮 click 继续 `stopPropagation()`。

**理由**：避免与 document 共享 click 处理器及其他壳 'click' 逻辑干扰。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 350ms 内点击菜单项无响应 | 双 rAF 恢复 pointer-events，实际可点窗口通常 < 350ms 仅防误触 |
| 用户误点「首歌库」统计期望打开菜单 | 统计与用户区分层展示；仅头像为触发器 |
| 侧栏 `overflow: hidden` 裁切向上菜单 | 菜单在 bottom 容器内向上展开，与后台相同模式，实践中可接受 |
| 与 searchable-select 的 document click 共存 | 两段逻辑独立，无共享状态 |

## Migration Plan

1. 部署更新 `index.html`、`studio.css?v=19`、`frontend.js?v=40`（或更高），硬刷新前台页。
2. 手动验收：点击侧栏底部 **头像** → 菜单保持展开 → 点击各项 → 点击主内容区关闭 → 再次点击头像 toggle。

## Open Questions

- 若生产环境仍偶发闪退，可补充 Playwright 回归（`scripts/debug-user-menu.mjs`）并记录 `data/debug-front-user-menu.ndjson` 对比。
