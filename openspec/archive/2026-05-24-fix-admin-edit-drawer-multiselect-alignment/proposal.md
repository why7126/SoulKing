## Why

后台歌曲管理页「编辑歌曲」抽屉在 `optimize-admin-song-edit-drawer` 之后，原唱、作词、作曲、语言、标签均使用同一套 `multi-select` 下拉。当前 `admin-studio.css` 中 `.admin-edit-panel input { width: 100%; … }` 误作用于选项列表内的 checkbox，导致复选框被拉成整行宽、文字错位，三列艺人字段（`.adm-form-grid-3`）因列宽更窄问题更明显。需在不动业务逻辑的前提下修复样式，使选项列表整齐可读。

## What Changes

- **排除 checkbox / hidden**：编辑抽屉内文本框样式规则不得作用于 `type="checkbox"`、`type="hidden"`。
- **固定选项行 checkbox 布局**：为 `.artist-option`（及抽屉内等价选项行）的 checkbox 设定固定尺寸、`flex: 0 0 auto`、无文本框式 padding/边框，保证与名称左对齐。
- **统一列表行内边距（P1）**：抽屉内 `multi-select-meta-hint`、`multi-select-meta-row`、`artist-option` 左缘与行高协调，减少「行与行不齐」观感。
- **窄列下拉可读性（P1）**：三列艺人字段的下拉菜单设置合理 `min-width` 或允许相对触发器向右展开，避免 ~150px 列宽下选项严重挤压。
- 递增 `admin-studio.css`（及必要时 `styles.css`）静态资源 `?v=`。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充编辑抽屉多选下拉选项列表的视觉与布局要求（checkbox 与文案对齐、不受文本框样式污染）。

## Impact

- **前端**：`app/static/admin-studio.css`（主改动）、可选 `app/static/styles.css`（通用 `.artist-option input` 加固）、`app/static/admin.html`（缓存版本）。
- **后端 / API**：无。
- **JS**：无（五个 `render*MultiSelect` 保持现状）。
