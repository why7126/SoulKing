## 1. 后端 API 与数据模型

- [x] 1.1 新增 `SongListPageOut`（`items`、`total`、`library_total`），将 `GET /songs` 响应改为该结构
- [x] 1.2 在 `list_songs` 中计算筛选后 `total` 与全库 `library_total`，再对结果切片填入 `items`
- [x] 1.3 从 `Album` 模型删除 `year` 字段；在 `_schema_migrations` 中增加删除 `albums.year` 的迁移
- [x] 1.4 清理代码中对 `Album.year` 的读写（含 schema、services、导入逻辑若有）

## 2. 后台列表 UI

- [x] 2.1 更新 `admin.html` 表头：按 spec 列顺序定义 th；移除年份、封面、状态、歌词列；为可排序列绑定 `data-sort`
- [x] 2.2 重写 `renderSongs` 行模板：独立列展示原唱、作词、作曲、语言、标签、时长、发行日期、创建/更新时间；歌曲列仅标题
- [x] 2.3 操作列：主区编辑、播放、下载；删除保留在更多菜单
- [x] 2.4 编辑抽屉：删除年份输入与封面占位；发行日期与 `release_date` 字段对齐
- [x] 2.5 调整 `admin-studio.css` 列宽与横向滚动以适配列数增加

## 3. 服务端分页与总数

- [x] 3.1 `loadSongs` 组装筛选 query（含 `tag_ids` 名称解析）及 `offset`/`limit`，解析 `{ items, total, library_total }`
- [x] 3.2 翻页、改每页条数、筛选/排序/关键词变更时重置页码并调用 `loadSongs`；移除对 `songsAfterQuickFilters` + 客户端 slice 的依赖
- [x] 3.3 页脚增加「共 N 首」文案元素；`updateAdminStats` 使用 `library_total` 填充音乐总数
- [x] 3.4 `renderPagination` 使用 API 返回的 `total` 计算总页数

## 4. 其它客户端兼容

- [x] 4.1 更新 `frontend.js` 中 `/songs` 消费为 `response.items`（及必要时保留 `total`）
- [x] 4.2 更新 `app.js` 中 `/songs` 消费为 `response.items`

## 5. 发布与验收

- [x] 5.1 递增 `admin.html` / `admin.js` 的 `?v=` 缓存版本
- [x] 5.2 手动验收：列顺序与字段、分页与总数、筛选后 total、全库 music 总数、编辑/播放/下载、无年份封面列、数据库无 `albums.year`
