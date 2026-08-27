## 1. 共享模块

- [x] 1.1 新增 `app/static/searchable-select.js`：实现 `ensureSearchableSelect`、`refreshSearchableSelectOptions`、`syncSearchableSelectTrigger`；多选行用 `div`+行点击；checkbox `id` 使用 `${selectId}-opt-${optionIndex}`；导出供前台/后台 import
- [x] 1.2 在 `index.html`、`admin.html` 以 module 方式在 `frontend.js` / `admin.js` 之前加载（或由各入口 `import` 该模块）

## 2. 前台接入

- [x] 2.1 从 `frontend.js` 删除重复的 searchable-select 实现，改为 `import` 共享模块
- [x] 2.2 确认 `renderFilterOptions` / 筛选 `change` 监听链无需改动；验证 `filterDropdownSelectedRawValues` 仍可用

## 3. 后台接入

- [x] 3.1 从 `admin.js` 删除重复的 searchable-select 实现，改为 `import` 共享模块
- [x] 3.2 确认 `populateQuickFilterOptions`、`loadSongs` 等调用点正常

## 4. 验证

- [x] 4.1 手动验证前台：语言、风格（点击文案勾选非首项）、标签无回归；列表 API 参数正确
- [x] 4.2 手动验证后台：语言、风格快速筛选同上；原唱等中文 value 维度抽检一项
