## Context

前台（`index.html` + `studio.css`）与后台（`admin.html` + `admin-studio.css`）均在侧栏底部提供用户头像与下拉菜单。菜单 DOM 位于 `.sk-sidebar-bottom` / `.adm-sidebar-bottom` 内，默认样式为 `position: absolute; left: 6px; right: 6px; bottom: calc(100% + 6px)`。

侧栏收起时 shell 添加 `.is-sidebar-collapsed`，宽度变为 64px。当前实现（`fix-collapsed-user-menu-popout`）使用 `left: calc(100% + 8px)` 将菜单向右浮出轨道，虽解决中文逐字换行，但菜单水平伸出至主内容区底部，与固定播放器（`.studio-player`，`z-index: 50`）重叠。

用户确认采用新方案：收起侧栏时菜单不向右浮出，而是在头像上方弹出且左边缘与头像左边缘对齐。

## Goals / Non-Goals

**Goals:**

- 收起侧栏时，用户菜单在头像上方弹出，左边缘与头像左边缘对齐，菜单项横排可读。
- 菜单从空间布局上避开底部播放器区域，无需依赖提升 z-index。
- 前台与后台行为、视觉令牌一致。
- 展开侧栏时菜单布局与现网完全一致。

**Non-Goals:**

- 不改为 `position: fixed` + JS 坐标计算。
- 不修改 HTML 结构或 JavaScript 菜单开关逻辑。
- 收起态菜单内不恢复用户名/meta 行。
- 不调整导航项、顶栏等其它收起态元素。

## Decisions

### 1. 收起态菜单左对齐头像（替代向右浮出）

在 `.app-shell.is-sidebar-collapsed` 下覆盖：

| 属性 | 展开（保持现状） | 收起（新） |
|------|------------------|------------|
| `left` | `6px` | `calc(50% - 18px)` |
| `right` | `6px` | `auto` |
| `width` / `min-width` | 由 left/right 拉伸 | `width: max-content; min-width: 160px` |
| `bottom` | `calc(100% + 6px)` | 不变 |
| `white-space` | （默认） | 菜单项 `nowrap` |

`18px` 为头像宽度（36px）的一半。收起态 `.sk-user-row` / `.adm-user-row` 已 `justify-content: center`，头像居中；菜单与 user-row 同属 `.sidebar-bottom` 的定位上下文，`calc(50% - 18px)` 使菜单左缘与头像左缘对齐。

**理由：** 菜单仍在头像上方垂直弹出，不向右浮出至播放器所在高度；`min-width` 保证横排可读。纯 CSS，改动面最小。

**备选：**
- 保留 `left: calc(100% + 8px)` + 提升 z-index — 已证实仍与播放器竞争层叠，弃用。
- 将菜单 DOM 移入 `.sk-user-row` — 需改 HTML，超出范围。

### 2. 定位上下文仍为 sidebar-bottom

菜单继续 `position: absolute`，相对 `position: relative` 的 bottom 区块定位。不移动 DOM。

**理由：** 与现有 z-index（30）及展开态行为一致；`overflow: visible` 已在收起态 bottom 区块设置。

### 3. 双文件对称修改

- `app/static/studio.css` — `.front-app .app-shell.is-sidebar-collapsed .sk-user-menu`
- `app/static/admin-studio.css` — `.admin-app .app-shell.is-sidebar-collapsed .adm-user-menu`

### 4. 不提升 z-index

新布局下菜单垂直位置在播放器之上，自然避开遮挡。收起态菜单保持 `z-index: 30`，不引入针对播放器的 z-index 覆盖。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 菜单 min-width 超出侧栏右缘，与主内容轻微重叠 | 可接受（菜单在侧栏上方区域，非播放器高度）；必要时 `min-width: min(160px, calc(100vw - 80px))` |
| 头像尺寸变更导致对齐偏移 | 头像固定 36px；若未来变更须同步更新 `18px` 偏移或改用 CSS 变量 |
| 仅修一侧 CSS 导致前后台不一致 | tasks 要求两处同步修改并分别验收 |

## Migration Plan

1. 修改 `studio.css`、`admin-studio.css`：将收起态 `left: calc(100% + 8px)` 替换为 `left: calc(50% - 18px)`。
2. 本地打开前台/后台 → 收起侧栏 → 打开用户菜单 → 确认左对齐头像、横排可读、不被播放器遮挡。
3. 归档时更新 `openspec/specs/sidebar-user-menu-popout/spec.md` 主 spec。
4. 无数据迁移、无 API 变更；回滚即恢复 `calc(100% + 8px)` 规则。

## Open Questions

（无。方案已在 explore 阶段与用户确认。）
