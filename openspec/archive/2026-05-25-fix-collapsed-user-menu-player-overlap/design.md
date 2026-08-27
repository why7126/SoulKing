## Context

前台与后台均已实现收起侧栏时用户菜单向右浮出（`fix-collapsed-user-menu-popout` / 方案 A）。菜单 DOM 仍在 `aside.app-sidebar` 内，使用 `position: absolute`；底部播放器为 `position: fixed`，前台 `z-index: 50`、后台 `#adminStudioPlayer` 为 `z-index: 40`。用户菜单默认 `z-index: 30`。

`app-shell` 为 flex 布局：`aside` 在 DOM 中先于 `app-main-wrap`，后者内的 fixed 播放器会叠在侧栏之上。收起后菜单水平伸出至主内容区底部，与播放器在视口重叠，仅提高菜单自身 `z-index` 无法越过 `app-main-wrap` 这一 flex 兄弟的绘制顺序。

## Goals / Non-Goals

**Goals:**

- 收起侧栏并打开用户菜单时，菜单完整显示在底部播放器/试听条之上，所有菜单项可点击。
- 展开侧栏时层叠行为与现网一致。
- 继续采用纯 CSS，不修改 HTML/JS。

**Non-Goals:**

- 不改为 `position: fixed` + JS 坐标（方案 C）。
- 不调整播放器 `z-index` 或布局（避免影响进度条、音量等交互层级）。
- 不处理菜单打开时侧栏与主内容区其它非播放器重叠（已有 rail 浮层惯例）。

## Decisions

### 1. 收起态提升侧栏轨道的 stacking，而非仅提高菜单 z-index

在 `.app-shell.is-sidebar-collapsed` 下为侧栏根节点增加：

```css
position: relative;
z-index: 55; /* 前台：高于 .studio-player (50) */
```

后台对称使用 `z-index: 45`（高于 `#adminStudioPlayer` 的 40）。

**理由：** flex 兄弟的绘制顺序导致 `app-main-wrap` 整体压在 `aside` 之上；必须让收起态侧栏参与更高层级的 stacking，向右伸出的菜单才能盖过 fixed 播放器。

**备选：** 仅将 `.sk-user-menu` 提到 `z-index: 60` — 在现有 DOM 结构下无效，已排除。

### 2. 收起态菜单保留相对 bottom 区块的 z-index: 30（可选微调）

侧栏轨道提升后，菜单可继续 `z-index: 30`；若与其它侧栏内浮层冲突，可在收起态将菜单设为 `z-index: 1`（相对侧栏内）或保持 30。实现时以「菜单在播放器之上」为准，不强制改菜单数值。

### 3. 双文件对称修改

- `app/static/studio.css` — `.front-app .app-shell.is-sidebar-collapsed .app-sidebar`（或已有 `.sk-studio-sidebar` 选择器）
- `app/static/admin-studio.css` — `.admin-app .app-shell.is-sidebar-collapsed .app-sidebar`

**理由：** 与 popout 变更一致，前后台样式分离、规则对称。

### 4. z-index 刻度与模态层隔离

| 层 | 现网 z-index | 收起态侧栏目标 |
|----|-------------|----------------|
| 用户菜单 | 30 | （随侧栏，不必须改） |
| 后台播放器 | 40 | 侧栏 45 |
| 前台播放器 | 50 | 侧栏 55 |
| 顶栏 | 80 | 不变（主内容区内） |
| 抽屉/模态 | 200+ | 不变，侧栏仍低于模态 |

**理由：** 避免侧栏盖住全局模态；仅解决与底部播放条的冲突。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 收起态 64px 侧栏条盖住主内容左下角一小条 | 可接受（rail 惯例）；仅收起态生效 |
| 侧栏 z-index 高于表格 sticky 列 | sticky 在主内容区内，与侧栏横向不重叠 |
| 展开态误加 z-index | 选择器限定 `.is-sidebar-collapsed` |

## Migration Plan

1. 修改 `studio.css`、`admin-studio.css` 收起态侧栏 `z-index`。
2. 本地前台/后台：收起侧栏 → 打开用户菜单 → 确认不被播放器遮挡、项可点击。
3. 无 API/数据变更；回滚即删除新增规则。

## Open Questions

（无）
