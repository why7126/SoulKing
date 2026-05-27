## 1. DOM 结构调整（index.html）

- [x] 1.1 删除 `#songBrowseSection` 内 Tab 栏（`.sk-library-tabs`）与「智能排序」按钮（`#btnSmartSort`）及视图切换占位按钮
- [x] 1.2 将搜索框从 `#headerSearchLibrary` 复制/迁移至音乐库内容区，新建 `studio-library-toolbar` 一行布局：搜索 wrap + 「更多筛选」+ 「重置」
- [x] 1.3 重构 `#frontFilterSection` 为六维筛选面板（原唱、作词、作曲、标签、格式、语言），DOM 结构与后台 `adm-filters-panel` 对齐
- [x] 1.4 更新 `<thead>` 列为：#、歌曲、原唱、作词、作曲、专辑、语言、标签、格式、时长、发行日期、操作（保留 `#` 序号列）
- [x] 1.5 递增 `index.html` / `frontend.js` / `studio.css` 的 `?v=` 缓存版本

## 2. 样式（studio.css）

- [x] 2.1 新增 `.studio-library-toolbar`、`.studio-library-filters-panel` 样式，参考 `admin-studio.css` 的 `adm-toolbar` / `adm-filters-panel` 一行布局与间距
- [x] 2.2 为新增表格列设置 `min-width`、文本 ellipsis 与 `.song-table-wrap` 横向滚动
- [x] 2.3 删除或清理 Tab 栏、智能排序相关无用样式（`.sk-library-tabs` 等）
- [x] 2.4 音乐库视图下隐藏顶栏 `#headerSearchLibrary` 的样式规则（如 `.studio-root.is-library-view`）

## 3. 脚本逻辑（frontend.js）

- [x] 3.1 移除 `state.libraryTab`、Tab 切换事件监听、`#btnSmartSort` 点击处理
- [x] 3.2 更新 `els` 引用：新增内容区搜索框与三个艺人筛选 select；调整筛选 toggle/reset 按钮绑定
- [x] 3.3 扩展 `loadFrontFilters` / `populateFrontFilterSelects`：填充原唱、作词、作曲选项（复用 `/admin/filter-options`）
- [x] 3.4 扩展 `loadSongs` 查询参数：追加 `lead_artists`、`lyricists`、`composers`；六维筛选变更时重新请求
- [x] 3.5 重写 `songRowInnerHtml` 输出 12 列；保留首列 `#` 序号（`pageOffset + index + 1`）；引入 `formatRoleNamesCell` 与发行日期格式化
- [x] 3.6 更新 `renderSongList` 空态/错误态 `colspan` 为 12
- [x] 3.7 实现视图切换时顶栏搜索与内容区搜索的显隐；更新 ⌘K / Ctrl+K 快捷键聚焦目标
- [x] 3.8 对齐「更多筛选」按钮文案与 `aria-expanded` 切换逻辑（展开/收起），重置按钮在有活跃筛选时显示

## 4. 验收

- [x] 4.1 手动验证：音乐库无 Tab、无智能排序，搜索与「更多筛选」同一行
- [x] 4.2 手动验证：六维筛选展开/重置/服务端过滤生效
- [x] 4.3 手动验证：表格 12 列（含 `#` 序号）数据正确，操作列试听/加入歌单/下载可用
- [x] 4.4 手动验证：顶栏搜索在音乐库视图隐藏，其它视图（如歌单）顶栏搜索仍正常
