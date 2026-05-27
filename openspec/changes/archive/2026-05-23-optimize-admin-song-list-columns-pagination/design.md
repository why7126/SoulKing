## Context

后台歌曲管理页（`admin.html` + `admin.js`）当前表格列为：勾选、歌曲（含时长副文案）、艺人、专辑、年份、格式、歌词图标、封面占位、元数据进度、状态、操作。数据通过 `GET /songs?limit=500` 一次拉取，快速筛选在客户端 `songsAfterQuickFilters` 内完成，分页仅对内存中筛选结果 `slice`。

服务端 `GET /songs` 已支持 `offset`、`limit` 及多维筛选查询参数，但响应为裸数组且无 `total`。`Album` 模型含未在列表使用的 `year` 列；歌曲发行信息以 `songs.release_date` 存储，编辑抽屉另有「年份」数字框与 `release_date` 双向同步。

## Goals / Non-Goals

**Goals:**

- 表格列与顺序与产品定义一致；操作列提供编辑、播放、下载。
- 移除列表/编辑 UI 中的年份、封面；删除 `albums.year` 列。
- 服务端分页：筛选、排序、翻页均由 API 完成；响应含筛选后 `total` 与全库 `library_total`（或等价字段）。
- 页脚展示「共 N 首」；顶部「音乐总数」展示全库歌曲数。

**Non-Goals:**

- 前台播放器列表 UI 列调整（仅适配 API 响应形态若共用 `/songs`）。
- 真实封面图存储与展示（S3 `music-covers` 桶配置保留，不在本变更实现封面业务）。
- 重写列表查询为纯 SQL 分页（可仍先内存筛选后切片，但须返回正确 `total`）。

## Decisions

### 1. 列表 API 响应包裹为分页对象

**选择**：`GET /songs` 返回 `{ "items": SongOut[], "total": number, "library_total": number }`（Pydantic `SongListPageOut`）。

**理由**：调用方需要筛选后总数与全库总数；裸数组无法扩展。

**替代**：保留数组并增加响应头 `X-Total-Count` —— 前台/脚本解析不一致，故不采用。

**兼容**：同步更新 `admin.js`、`frontend.js`、`app.js` 中 `/songs` 消费处（取 `items`）；本变更 tasks 包含三处。

### 2. 后台筛选与分页一律走服务端

**选择**：`loadSongs` 组装与 `main.list_songs` 一致的 query（`keyword`、`lead_artists`、`lyricists`、`composers`、`formats`、`languages`、`tag_ids`、`sort_by`、`sort_order`、`offset`、`limit`）；标签名在客户端解析为 `tag_ids`。

**理由**：避免 `limit=500` 截断导致筛选与总数不准。

**替代**：继续客户端筛选 —— 与大曲库及「显示总数量」目标冲突。

### 3. 移除 `albums.year`

**选择**：从 `Album` 模型删除 `year`；在 `main.py` 既有 `_schema_migrations` 机制中登记迁移，对 SQLite 执行 `ALTER TABLE albums DROP COLUMN year`（若方言不支持则重建表，与项目现有迁移风格一致）。

**理由**：用户要求数据库不再保留年份；发行时间以 `songs.release_date` 为准。

**编辑表单**：删除 `releaseYearInput`；保留/强化 `release_date` 文本字段（若当前仅年份框，改为发行日期输入并与 `release_date` 同步）。

### 4. 表格列与操作

**选择**：表头固定 14 列数据列 + 勾选 + 操作；时长、发行日期、创建/更新时间使用与后台一致的格式化函数；元数据列保留完成度条；删除「状态」「歌词」「封面」「年份」列。

**操作**：行内图标/按钮 — 编辑、播放（`canWebPreview` 时可用）、下载；删除保留在「更多」菜单。

### 5. 总数展示

**选择**：

- `total`：当前请求参数下筛选后的歌曲条数（分页计算依据）。
- `library_total`：库内 `songs` 表行数（忽略筛选）。
- 页脚：`共 {total} 首`（有筛选时可附「已筛选」类文案）。
- `statSongCount`：使用 `library_total`。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| **BREAKING** `/songs` 响应形态变更导致旧脚本失败 | 同 PR 更新全部调用方；tasks 验收 |
| 列表仍在内存中过滤，大数据量性能差 | 与现实现一致；`total` 仍准确；后续可单独做 SQL 优化 |
| SQLite `DROP COLUMN` 兼容性 | 沿用项目迁移模式，必要时表重建 |
| 标签筛选由名称改 ID 传参，名称重名/不存在 | 与现有 API `tag_ids` 行为一致；无效 ID 静默忽略 |

## Migration Plan

1. 部署前备份数据库。
2. 应用启动时运行迁移：删除 `albums.year`。
3. 部署后端 + 静态资源（递增 `admin.js` / `admin.html` 的 `?v=`）。
4. 验证：列表列顺序、分页、总数、编辑保存、前台列表仍可加载。

**回滚**：恢复上一版本代码；若已删列需从备份恢复或接受 `year` 列缺失（通常可空列忽略）。

## Open Questions

- 发行日期在编辑抽屉是否已有独立 `release_date` 输入框，或需从「年份」改为日期文本 —— 实现时以 `admin.html` 现有字段为准，确保与列表「发行日期」列同源。
- 「元数据」列是否继续用完成度百分比 —— 默认保留现有 `metadataCompleteness` 逻辑。
