## Why

前台音乐库与后台歌曲管理页的「更多筛选」使用可搜索多选下拉（`searchable-select`）渲染 checkbox 行。当前实现用 `option.value` 经 ASCII 清洗后作为 checkbox 的 `id`，中文选项名（语言、风格、艺人名等）会生成**重复 id**；前台还用 `<label for="...">` 关联，点击文字会激活文档中第一个同名 id，表现为「点哪项都像选中第一项」。标签筛选用数字 `tag.id` 作 value 故正常。需在前后台统一交互与 id 生成，恢复多选勾选可靠性。

## What Changes

- **统一筛选多选 UI 逻辑**：抽取或对齐 `refreshSearchableSelectOptions`（及绑定逻辑），前台 `frontend.js` 与后台 `admin.js` 使用同一套行结构、点击区域与 checkbox id 规则。
- **唯一 checkbox id**：按选项在 `<select>` 中的下标（或等价稳定键）生成 id，禁止仅用清洗后的 `value` 字符串。
- **可靠点击命中**：采用与后台一致的「行容器 + 点击行切换本行 checkbox」模式，或去掉错误的 `label[for]` 与重复 id；点击标签文字与 checkbox 均应切换**当前行**对应 `<option>` 的 `selected` 状态。
- **不改变筛选 API 契约**：`languages`、`genre_ids`、`tag_ids`、艺人名称等查询参数与选项 value 语义保持不变。
- **回归范围**：前台语言、风格及中文 value 的艺人/格式等维度；后台语言、风格、标签、艺人等快速筛选。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充可搜索多选筛选控件在中文/非 ASCII 选项值下的勾选交互与唯一标识要求。

## Impact

- **前端**：`app/static/frontend.js`（`refreshSearchableSelectOptions`、`ensureSearchableSelect`）；可选小改 `app/static/admin.js` 若未完全抽取共用。
- **后端 / API**：无变更。
- **OpenSpec**：`openspec/specs/web-static-client-shells/spec.md` 增量需求。
