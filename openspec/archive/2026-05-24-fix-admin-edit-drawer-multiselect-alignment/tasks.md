## 1. 修复 checkbox 被文本框样式污染

- [x] 1.1 将 `admin-studio.css` 中 `.admin-edit-panel input` 改为排除 `checkbox` 与 `hidden`（`:not([type="checkbox"]):not([type="hidden"])`）
- [x] 1.2 新增 `.admin-edit-panel .multi-select-menu .artist-option input[type="checkbox"]` 规则：16px 固定尺寸、`flex: 0 0 16px`、无文本框 padding/边框

## 2. 列表行对齐与窄列菜单

- [x] 2.1 在 `.admin-edit-panel .multi-select-menu` 内统一 `meta-hint` / `meta-row` / `artist-option` 左内边距，并去掉 `artist-option` 负 margin 与 `calc(100% + 8px)` 宽度（仅抽屉作用域）
- [x] 2.2 为 `.admin-edit-panel .multi-select-menu` 设置 `min-width: 200px`（三列内 `.adm-form-grid-3` 可用 220px）

## 3. 验收与发布

- [x] 3.1 手动验证：原唱/作词/作曲/语言/标签五个下拉选项行 checkbox 与文字左对齐；搜索框仍全宽
- [x] 3.2 递增 `admin.html` 中 `admin-studio.css` 的 `?v=` 缓存参数
