## 1. DOM 标记

- [x] 1.1 在 `admin.html` 歌曲表头第 2 列 `<th>` 添加 `col-title` 类
- [x] 1.2 在 `admin.js` `renderSongs` 中歌曲 `<td>` 添加 `col-title` 类

## 2. 冻结列 CSS

- [x] 2.1 在 `#admin-page-music .adm-songs-table` 定义 `--adm-sticky-check-width`、`--adm-sticky-title-width` 变量
- [x] 2.2 为 `col-check` 设置固定宽度与 `left: 0` sticky（校验与变量一致）
- [x] 2.3 为 `col-title`  thead th / tbody td 添加 `position: sticky; left: var(--adm-sticky-check-width)`、固定宽度、分隔 box-shadow、文本 ellipsis
- [x] 2.4 更新 z-index 分层：中间列 tbody td `z-index: 0`；冻结数据列 11–13；冻结列表头 21–25；中间列表头低于冻结表头
- [x] 2.5 确认 `border-collapse: separate` 在 `.adm-songs-table` 生效，tbody 保留 `isolation: isolate`

## 3. 不透底与行态背景

- [x] 3.1 所有 tbody `td` 施加实色 `background-color: var(--adm-sticky-bg)`（含中间列）
- [x] 3.2 将 `--adm-sticky-bg-hover` 改为不透明色；hover / `is-active` 时对每个 `td` 设置背景，tr 背景设为 transparent
- [x] 3.3 冻结列 thead th 使用实色表头背景（`var(--adm-bg)` 或等价），与数据列背景 clip 一致

## 4. 验收与发布

- [x] 4.1 浏览器手动验证：横向滚动中间位置时左侧勾选+歌曲、右侧操作冻结且中间列文字不透底
- [x] 4.2 验证 hover、`is-active` 选中态下冻结列无叠字、无透底
- [x] 4.3 递增 `admin.html` 中 `admin-studio.css`（及若改动的 `admin.js`）`?v=` 缓存版本
