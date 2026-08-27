## Context

前台（`studio.css`）与后台（`admin-studio.css`）的用户菜单均使用 `position: absolute`，相对 `.sk-user-row` / `.adm-user-row` 定位。展开侧栏时：

```css
bottom: calc(100% + 6px);
```

即菜单底边与头像行顶边之间固定 **6px** 间隙。

收起侧栏时，当前实现为：

```css
bottom: calc(100% + var(--*-player-total-h) + 6px);
```

其中 `--sk-player-total-h` / `--adm-player-total-h` 为底部播放器/试听条的总高度（约 80–100px）。该偏移是为避免菜单与固定定位的播放器重叠而引入，但导致菜单与头像间距被播放器高度「撑开」，与展开态视觉不一致。

此前 `align-collapsed-user-menu-item-avatar` 的设计意图即为收起态也使用 `bottom: calc(100% + 6px)`；本变更将其与现网实现对齐。

## Goals / Non-Goals

**Goals:**

- 收起侧栏时，用户菜单与头像之间的垂直间隙与展开侧栏时一致（均为 6px）。
- 保持收起态左对齐头像、`min-width`、`white-space: nowrap` 等既有规则。
- 纯 CSS 修改，不涉及 HTML/JS。

**Non-Goals:**

- 不改变展开侧栏时的菜单布局。
- 不恢复向右浮出侧栏轨道的方案。
- 不重构播放器或侧栏底部区域的整体布局。
- 不在本变更中引入 JavaScript 动态定位或 Portal。

## Decisions

### 1. 移除收起态 `bottom` 中的播放器高度偏移

**选择**：将收起态 `bottom` 统一为 `calc(100% + 6px)`，与展开态共用同一间隙常量。

**理由**：用户菜单的定位锚点是头像行（`.sk-user-row` / `.adm-user-row`），间隙应以头像为参照而非播放器。展开态已证明 6px 间隙在侧栏底部可用；收起态左对齐头像后，菜单仍在侧栏轨道内或紧贴轨道，与播放器重叠风险低于此前向右浮出方案。

**备选方案**：

| 方案 | 说明 | 不采用原因 |
|------|------|------------|
| 保留 `--*-player-total-h` 偏移 | 菜单始终浮于播放器上方 | 与头像间距过大，不符合本变更目标 |
| 用 `margin-bottom` 替代 `bottom` 偏移 | 分离间隙与定位 | 增加复杂度，无额外收益 |
| JS 动态计算间隙 | 运行时测量 | 违反纯 CSS 约束，过度设计 |

### 2. 不新增 CSS 自定义属性

**选择**：直接复用展开态已有的 `6px` 字面量，不抽取为 `--sk-user-menu-gap` 等变量。

**理由**：展开态与收起态仅两处各改一行；抽取变量需同步修改展开态规则，超出本变更最小范围。

### 3. 播放器遮挡由既有 spec 场景覆盖

**选择**：本变更聚焦间隙一致性；`sidebar-user-menu-popout` 中「不被播放器遮挡」的验收场景仍保留，若移除偏移后菜单与播放器重叠，需依赖侧栏 `overflow: visible` 与菜单在侧栏左缘的定位自然避开，或在后续变更中单独处理 z-index。

**理由**：左对齐头像后菜单主要向上展开于侧栏窄轨道上方，与全宽播放器的水平重叠面小于向右浮出方案；用户明确要求间隙一致，优先满足该 UX 目标。

## Risks / Trade-offs

- **[Risk] 收起态菜单可能与底部播放器在视口上部分重叠** → 菜单位于侧栏左缘、向上弹出；若实测仍有遮挡，可在后续变更中评估提升收起态 `z-index`（不纳入本变更）。
- **[Risk] 前台与后台播放器高度不同导致视觉微差** → 间隙以头像为锚、与播放器无关，两壳行为一致。
- **[Trade-off] 放弃「菜单永远在播放器上方」的硬约束** → 换取与展开态一致的紧凑间距；符合用户方案 A 第 3 点优先级。

## Migration Plan

1. 修改 `studio.css` 中 `.front-app .app-shell.is-sidebar-collapsed .sk-user-menu` 的 `bottom`。
2. 修改 `admin-studio.css` 中 `.admin-app .app-shell.is-sidebar-collapsed .adm-user-menu` 的 `bottom`。
3. 手动验收：前台/后台分别切换收起/展开，打开用户菜单，目测或 DevTools 测量菜单底边与头像顶边间距均为 6px。
4. 回滚：恢复 `var(--*-player-total-h)` 偏移即可。

## Open Questions

（无）
