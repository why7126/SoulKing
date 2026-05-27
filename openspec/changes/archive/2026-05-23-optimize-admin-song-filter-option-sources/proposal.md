## Why

后台歌曲管理页「更多筛选」中，原唱、作词、作曲、标签、语言五个维度的下拉选项目前主要从**当前曲库歌曲**推导（标签仅部分合并标签管理数据）。这会导致：曲库中尚未出现的艺人/标签/语言无法被筛选；与管理后台「艺人管理」「标签管理」「语言管理」维护的权威数据不一致；用户无法按完整参考数据召回歌曲。需要将筛选项的数据源改为各管理模块的列表，并与艺人类型（歌手 / 作词 / 作曲）对齐。

## What Changes

- **原唱**：筛选项取自艺人管理（`/people`）中 `types` 包含「歌手」的艺人名称，按名称升序。
- **作词**：筛选项取自艺人管理中 `types` 包含「作词」的艺人名称。
- **作曲**：筛选项取自艺人管理中 `types` 包含「作曲」的艺人名称。
- **标签**：筛选项仅取自标签管理（`/tags`）列表，不再从歌曲 `tags` 字段合并推导。
- **语言**：筛选项仅取自语言管理（`/languages`）列表，不再从歌曲 `language` 字段推导。
- **格式**：保持现有逻辑（从曲库文件格式推导），本变更不修改。
- 在 `populateQuickFilterOptions` 刷新时机上，于 `loadPeople` / `loadTags` / `loadLanguages` 完成后同步刷新上述五个维度；已选值若仍存在于新选项列表中则保留。
- 列表过滤逻辑不变：选项值为名称字符串，与歌曲元数据字段匹配；同维度 OR、跨维度 AND。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充后台歌曲管理页快速筛选各维度**选项来源**要求（艺人按类型、标签与语言取自参考数据管理列表）。

## Impact

- **前端**：`app/static/admin.js`（`populateQuickFilterOptions`、必要时 `loadFilterOptions` 调用链与初始化顺序）。
- **后端 / API**：无变更（复用已有 `/people`、`/tags`、`/languages`）。
- **OpenSpec**：`openspec/specs/web-static-client-shells/spec.md` 增量需求。
