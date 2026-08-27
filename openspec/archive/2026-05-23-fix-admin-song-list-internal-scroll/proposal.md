## Why

歌曲管理页列数较多（14 列以上），在常见桌面视口下表格总宽度常超出可视区域；同时每页可展示 20–100 条记录。若列表区域未形成独立的纵/横向滚动容器，用户会出现整页滚动、右侧列被裁切、或无法浏览完整行数据等问题，影响日常筛选与批量操作效率。

## What Changes

- **列表区域独立滚动**：歌曲表格 MUST 在 `.adm-table-scroll`（或等价容器）内同时支持纵向与横向滚动；页面级（`body` / 主内容 wrap）不因列表数据而出现纵向滚动条。
- **完整字段可浏览**：用户通过横向滚动可访问所有数据列（含发行日期、元数据、创建/更新时间等中间列）；通过纵向滚动可浏览当前页全部行。
- **表头随纵滚冻结**：纵向滚动时表头保持在滚动容器顶部可见（sticky thead），便于对照列名。
- **滚动条可见性**：内容溢出时滚动容器应呈现可操作的滚动条（含 WebKit / Firefox 细滚动条样式），避免「内容被裁切但无滚动提示」。
- **与表底分页协同**：表底分页栏固定在列表区底部、不参与表格内部滚动；滚动仅作用于表格主体区域。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充/强化歌曲管理页列表容器双轴滚动、表头 sticky、全列可访问及滚动条可见性要求。

## Impact

- **前端**：`app/static/admin.html`（必要时调整 DOM 层级）、`app/static/admin-studio.css`（主改动）、`app/static/styles.css`（消除与旧 `.admin-table-wrap` 规则的冲突）。
- **后端 / API**：无变更。
- **OpenSpec**：`openspec/specs/web-static-client-shells/spec.md` 增量。
