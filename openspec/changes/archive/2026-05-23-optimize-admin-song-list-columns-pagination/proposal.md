## Why

后台「歌曲管理」列表当前列信息与产品期望不一致：缺少作词、作曲、语言、标签、时长、发行日期、创建/更新时间等关键字段；存在无实际数据的「封面」列与易与「发行日期」混淆的「年份」列；分页仅在客户端对已加载的最多 500 条记录切片，无法在筛选后展示真实曲库总量，大曲库下体验与性能均不足。

## What Changes

- **列表列与顺序**：按固定顺序展示——歌曲、原唱、作词、作曲、专辑、语言、标签、格式、时长、发行日期、元数据、创建时间、更新时间、操作（编辑、播放、下载）；移除「状态」「歌词」图标列及「艺人」合并列（原唱单独展示）。
- **移除年份与封面**：
  - 列表表头与行渲染删除「年份」「封面」列。
  - 编辑抽屉删除「年份」数字输入与封面占位区域。
  - **BREAKING**：删除 `albums.year` 数据库列及相关读写；歌曲发行信息仅保留 `songs.release_date`（发行日期列展示该字段）。
- **服务端分页与总数**：
  - 列表请求使用 `offset`、`limit` 与当前筛选、排序参数；响应除当前页数据外返回匹配筛选条件的**总条数**。
  - 分页控件驱动重新拉取当前页；页脚或列表区域展示「共 N 首」等总数文案。
  - 顶部「音乐总数」统计在歌曲管理页展示**全库**歌曲数（可与筛选总数区分：筛选时展示「筛选结果 N 首」）。
- **操作列**：主操作区提供编辑、播放（可播放时）、下载；删除等次要操作可保留在「更多」菜单。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：后台歌曲管理页表格列定义、操作按钮、分页交互与总数展示。
- `song-catalog-and-metadata`：列表 API 分页响应形态（含 `total`）；移除专辑 `year` 字段；发行日期为唯一发行时间字段。

## Impact

- **前端**：`app/static/admin.html`、`app/static/admin.js`、`app/static/admin-studio.css`（列宽、分页文案）。
- **后端**：`app/main.py`（`/songs` 响应结构）、`app/models.py`（`Album.year` 迁移删除）、`app/services.py` / schema 若引用专辑年份。
- **数据库**：Alembic 或项目既有迁移机制删除 `albums.year`。
- **OpenSpec**：`openspec/specs/web-static-client-shells/spec.md`、`openspec/specs/song-catalog-and-metadata/spec.md` 增量。
