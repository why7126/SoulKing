## Context

- 前台 `frontend.js` 与后台 `admin.js` 各自实现一套 `ensureSearchableSelect` / `refreshSearchableSelectOptions`，逻辑高度相似但不一致。
- 多选模式下为每个 `<option>` 动态生成 checkbox；`cb.id` 使用 `${selectId}-opt-${sanitize(value)}`，中文 `value` 清洗后常相同（如 `__`）。
- 前台使用 `<label for="id">` 包裹行，重复 `id` 导致点击文案命中错误选项；后台用 `<div>` + 行点击 `cb.click()`，交互相对正确但仍存在重复 `id`（无障碍与 DOM 无效）。
- 标签筛选用数字 id 作 value，故未暴露问题；语言、风格、艺人名等用中文名称作 value 易复现。

## Goals / Non-Goals

**Goals:**

- 前后台筛选多选下拉对**任意** `option.value`（含中文、特殊字符）勾选行为一致且正确。
- 点击行内 checkbox 或选项文案，仅切换**该行**对应 `<option>.selected`。
- 同一 `<select>` 内生成的 checkbox `id` 在文档内唯一。
- 尽量 DRY：单一实现来源，避免再次分叉。

**Non-Goals:**

- 不修改 `multi-select`（编辑抽屉元数据）组件——本变更仅针对 `searchable-select` 包裹的 `<select multiple>` 快速筛选。
- 不改变选项 value 语义（不强制全部改为 id，除非实现时发现抽取共用模块需要统一辅助函数）。
- 不新增构建步骤或 npm 依赖。

## Decisions

### 1. 抽取共享模块 `searchable-select.js`

**选择**：新建 `app/static/searchable-select.js`，导出 `ensureSearchableSelect`、`refreshSearchableSelectOptions`、`syncSearchableSelectTrigger`（及前台/后台已用的 `filterDropdownSelectedRawValues` 若可共用则一并导出或保留原位）。

**理由**：用户明确要求「前台+后台同一套逻辑」；两处 150+ 行重复，修一处即可覆盖全部筛选。

**备选**：只改前台对齐后台 div+click —— 仍有两份代码，后续易再漂移。

### 2. checkbox id 使用选项下标

**选择**：`cb.id = \`${selectId}-opt-${index}\``（`index` 为 `selectEl.options` 中的稳定下标；重建菜单时按当前 `filtered` 列表映射回 `r.opt`）。

**理由**：与 `value` 内容无关，中文/重复显示名均唯一。

**备选**：`encodeURIComponent(value)` —— 可读性差，极长 value 仍可能触及 id 限制。

### 3. 行交互：div + 行点击（不用 label[for]）

**选择**：多选行使用 `<div class="searchable-select-check-row">`，结构为 `[checkbox][span 文案]`；行 `click`（非 checkbox 目标）时 `cb.click()`；checkbox 上 `stopPropagation` 避免双触发。

**理由**：与当前后台行为一致，不依赖 `for` 与全局 id；点击区域覆盖整行。

### 4. 脚本加载顺序

**选择**：`admin.html` / `index.html` 在 `admin.js` / `frontend.js` 之前引入 `searchable-select.js`（`type="module"` 若现有为 module 则保持一致；若现有为普通 script 则用 IIFE 挂 `window` 或 ES module import）。

**理由**：最小侵入；需核对现有 static 是否已用 `import`（`frontend.js` 已从 `lrc.js` import，宜用 ES module）。

### 5. 验证矩阵

手动验证：前台语言、风格、原唱；后台语言、风格；各选 2 项、点文案、关开下拉、触发列表刷新。

## Risks / Trade-offs

- **[模块加载方式不一致]** → 读现有 `index.html`/`admin.html` script 标签，与 `lrc.js` 相同模式 export/import。
- **[抽取遗漏调用点]** → grep `refreshSearchableSelectOptions` / `ensureSearchableSelect` 全仓库。
- **[编辑抽屉不受影响]** → 明确不改动 `multi-select` 路径。

## Migration Plan

仅静态资源更新；部署后硬刷新即可。回滚：还原三文件（或两 JS + 删除新模块）。

## Open Questions

（无）
