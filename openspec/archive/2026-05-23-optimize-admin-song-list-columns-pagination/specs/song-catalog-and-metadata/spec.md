## ADDED Requirements

### Requirement: 歌曲列表分页响应形态

`GET /songs` 成功响应 SHALL 为 JSON 对象，包含：

- `items`：当前页的 `SongOut` 数组（与分页、筛选、排序参数一致）；
- `total`：满足当前请求中所有筛选与关键词条件后的歌曲总条数（用于分页，可大于 `items.length`）；
- `library_total`：曲库中歌曲记录总数（忽略本次请求的筛选参数）。

#### Scenario: 默认分页响应结构

- **GIVEN** 曲库中存在歌曲
- **WHEN** 客户端请求 `GET /songs` 并指定 `offset=0`、`limit=20`
- **THEN** 响应体为对象且包含 `items`、`total`、`library_total`
- **AND** `items` 长度不超过 20
- **AND** `total` 为通过筛选后的全集条数
- **AND** `library_total` 等于库内全部歌曲行数

#### Scenario: 筛选后 total 与 library_total 区分

- **GIVEN** 全库 100 首，其中 10 首满足请求中的原唱筛选
- **WHEN** 客户端携带该原唱筛选请求列表
- **THEN** `total` 为 10
- **AND** `library_total` 为 100

#### Scenario: 无匹配时 items 为空且 total 为零

- **GIVEN** 筛选条件无歌曲命中
- **WHEN** 客户端请求列表
- **THEN** `items` 为空数组
- **AND** `total` 为 0
- **AND** `library_total` 仍为全库条数

## MODIFIED Requirements

### Requirement: 列表排序与分页

服务端在内存中对已通过筛选的列表项按所选字段排序后，再按偏移与条数将结果放入响应的 `items`；同时将筛选后全集条数写入 `total`，将库内歌曲总数写入 `library_total`。

#### Scenario: 默认排序与分页

- **GIVEN** 客户端使用默认排序键与排序方向，并指定偏移与条数
- **WHEN** 请求列表
- **THEN** `items` 顺序与分页切片与请求参数一致
- **AND** `total` 反映筛选后全部条数而非仅当前页条数

## REMOVED Requirements

### Requirement: 专辑年份字段

**Reason**：产品以歌曲 `release_date` 作为唯一发行时间展示与编辑字段；`albums.year` 未在列表使用且与「年份」列一并移除。

**Migration**：部署时运行 schema 迁移删除 `albums.year` 列；历史年份数据不迁移至其他列（若曾写入专辑年份，由运维按需手工补全 `release_date`）。
