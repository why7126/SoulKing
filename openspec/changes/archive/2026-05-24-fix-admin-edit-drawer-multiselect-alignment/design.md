## Context

编辑抽屉（`#adminEditPanel`）内原唱、作词、作曲、语言、标签使用 `styles.css` 中的 `.multi-select` / `.artist-option` 结构；`admin-studio.css` 对 `.admin-edit-panel input` 统一设置了 `width: 100%` 与文本框 padding，未排除 checkbox。

三列艺人字段位于 `.adm-form-grid-3`（抽屉宽约 480px，每列 ~150px），下拉菜单 `left:0; right:0` 与触发器等宽，长选项名在 `white-space: nowrap` 下更易显得拥挤。

## Goals / Non-Goals

**Goals:**

- 选项列表内 checkbox 为固定小尺寸，与名称在同一行左对齐，不被文本框样式拉伸。
- 原唱 / 作词 / 作曲 / 语言 / 标签五个字段下拉列表视觉一致。
- 窄列下下拉仍可读（最小宽度或向右溢出）。

**Non-Goals:**

- 不重写 `render*MultiSelect` 或改 API。
- 不调整抽屉字段布局（不取消三列艺人）。
- 不修改前台或其它页面的 multi-select（除非共用规则且无副作用）。

## Decisions

### 1. 收窄 `admin-edit-panel input` 选择器

**选择**：

```css
.admin-app .admin-edit-panel input:not([type="checkbox"]):not([type="hidden"]),
.admin-app .admin-edit-panel select { ... }
```

**理由**：一行修复根因；搜索框、标题等仍保持全宽。

### 2. 抽屉内 checkbox 专用规则

**选择**：在 `admin-studio.css` 增加：

```css
.admin-app .admin-edit-panel .multi-select-menu .artist-option input[type="checkbox"] {
  width: 16px;
  height: 16px;
  flex: 0 0 16px;
  padding: 0;
  margin: 0;
  border: none;
  background: transparent;
  ...
}
```

**理由**：`.multi-select-option input` 已有 `flex: 0 0 auto`，但选项行类名为 `.artist-option`；后台作用域限定避免影响其它页面。

**备选**：改 JS 统一用 `.multi-select-option` —— 改动面大，不采纳。

### 3. 列表行对齐与负 margin

**选择**：在 `.admin-edit-panel .multi-select-menu` 内：

- 统一 `meta-hint` / `meta-row` / `artist-option` 的 `padding-left`（如 10px）。
- 将 `.artist-option` 的 `width: calc(100% + 8px)` 与 `margin: 0 -4px` 改为 `width: 100%; margin: 0`（仅抽屉作用域）。

**理由**：负 margin 在窄菜单中与 checkbox 拉伸叠加会放大错位。

### 4. 窄列菜单最小宽度

**选择**：`.admin-app .admin-edit-panel .multi-select-menu { min-width: 200px; }`；在 `.adm-form-grid-3 .multi-select` 下可设 `min-width: 220px`。菜单仍 `position: absolute`，允许向右超出列宽（不 `overflow: hidden` 裁切父级）。

**理由**：解决「接近 3」的列宽问题；220px 在 480px 抽屉内可接受。

**备选**：`position: fixed` + JS 定位 —— 复杂度高，暂不采用。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 菜单向右溢出抽屉 | `z-index: 50` 已有；必要时 `max-width: min(280px, 90vw)` |
| 其它 `checkbox` 在抽屉内需特殊样式 | 规则限定在 `.multi-select-menu` 内 |
| 与 `styles.css` 全局 `.artist-option` 冲突 | 后台用更高特异性 `.admin-app .admin-edit-panel` 覆盖 |

## Migration Plan

仅静态 CSS + `?v=` 缓存刷新，无数据迁移。

## Open Questions

（无）
