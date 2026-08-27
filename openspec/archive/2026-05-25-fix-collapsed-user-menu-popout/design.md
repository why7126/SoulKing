## Context

前台（`index.html` + `studio.css`）与后台（`admin.html` + `admin-studio.css`）均在侧栏底部提供用户头像与下拉菜单。菜单 DOM 位于 `.sk-sidebar-bottom` / `.adm-sidebar-bottom` 内，默认样式为：

- `position: absolute`
- `left: 6px; right: 6px`（宽度随父容器拉伸）
- `bottom: calc(100% + 6px)`（在头像行上方弹出）

侧栏收起时 shell 添加 `.is-sidebar-collapsed`，宽度变为 `--sidebar-w-collapsed`（64px）。收起态已隐藏 `.sk-user-meta` / `.adm-user-meta` 并将头像居中，但菜单仍受 64px 父级宽度约束，中文项逐字换行。

探索阶段已确认根因是宽度而非 `writing-mode`；方案 A 为纯 CSS，菜单向右浮出轨道，不改动 HTML/JS。

## Goals / Non-Goals

**Goals:**

- 收起侧栏时，用户菜单在侧栏右缘外弹出，菜单项横排可读。
- 前台与后台行为、视觉令牌一致（面板背景、圆角、阴影沿用现有变量）。
- 展开侧栏时菜单布局与现网完全一致。

**Non-Goals:**

- 不改为 `position: fixed` + JS 坐标计算（方案 C）。
- 收起态菜单内不恢复用户名/meta 行。
- 不改为纯图标菜单（方案 D）。
- 不调整导航项、顶栏 tier 按钮等其它收起态元素。

## Decisions

### 1. 收起态菜单锚定在侧栏右缘外侧（方案 A）

在 `.app-shell.is-sidebar-collapsed` 下覆盖：

| 属性 | 展开（保持现状） | 收起（新增） |
|------|------------------|--------------|
| `left` | `6px` | `calc(100% + 8px)` |
| `right` | `6px` | `auto` |
| `width` / `min-width` | 由 left/right 拉伸 | `min-width: 160px`（或 `width: max-content` + `min-width: 160px`） |
| `white-space` | （默认） | 菜单项 `nowrap` |

`bottom` 保持 `calc(100% + 6px)`，菜单仍在头像上方弹出，仅水平方向脱离窄轨道。

**理由：** 与 VS Code / Figma 等「窄 rail + 浮层」模式一致；改动面最小，无需改 `frontend.js` / `admin.js` 的开关逻辑。

**备选：** `position: fixed` + `getBoundingClientRect` — 更稳但过度工程；`min-width` 在侧栏内撑开 — 仍可能被裁切或压住左缘。

### 2. 定位上下文仍为 `.adm-sidebar-bottom` / `.sk-sidebar-bottom`

菜单继续 `position: absolute`，相对 `position: relative` 的 bottom 区块定位。收起态 `left: calc(100% + 8px)` 的 100% 指 bottom 区块宽度（与侧栏内容区一致），菜单整体出现在轨道右侧。

**理由：** 无需移动 DOM；与现有 z-index 层级一致。

### 3. 双文件对称修改

- `app/static/studio.css` — `.front-app .app-shell.is-sidebar-collapsed .sk-user-menu` 及可选 `.sk-user-menu-item`
- `app/static/admin-studio.css` — `.admin-app .app-shell.is-sidebar-collapsed .adm-user-menu` 及可选 `.adm-user-menu-item`

**理由：** 两壳样式分离，无共享 partial；复制规则可保证一致。

### 4. z-index 与 overflow

保持菜单 `z-index: 30`。实现后于浏览器中确认：`.app-shell` 的 `overflow: hidden` 不裁切向右伸入主内容区的菜单（菜单仍在 shell 盒内，预期安全）。若发现裁切，仅在侧栏或 bottom 区块增加 `overflow: visible`（最小范围），不作为首选。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 菜单与主内容区重叠 | 接受轻微重叠（常见 rail 行为）；`min-width` 控制在 ~160–180px |
| 小屏视口菜单超出右边界 | 使用 `min-width: min(180px, calc(100vw - 80px))` 等 clamp（实现时按需） |
| 仅修一侧 CSS 导致前后台不一致 | tasks 明确要求两处同步修改并分别验收 |

## Migration Plan

1. 修改 `studio.css`、`admin-studio.css` 收起态规则。
2. 本地打开前台/后台 → 收起侧栏 → 打开用户菜单 → 目视确认横排与不被裁切。
3. 无数据迁移、无 API 变更；回滚即删除新增 CSS 选择器。

## Open Questions

（无。方案 A 已在 explore 阶段与用户确认。）
