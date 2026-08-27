## Context

后台歌曲管理页（`admin-page-music`）当前状态：

- **操作列**（`renderSongs`）：`.adm-actions-inner` 内并列 `edit-quick`、`play-quick`、`download-quick` 三个 `.adm-icon-btn`，外加 `.table-more` 下拉（含编辑、删除）。与前台 `frontend.js` 中 `sk-row-more`「仅更多」模式不一致。
- **编辑抽屉**：`#filmTvInput` 位于 `.adm-hidden-filters`；`#releaseDateInput` 为 `type="text"`，`syncReleaseDateField` 直接赋值字符串。后端 `Song.film_tv`、`Song.release_date` 已支持读写。
- **播放器**：`footer.admin-player-compact` 含 `#adminNowPlaying`、上一首/下一首、`#adminPlayModeSelect` 与带 `controls` 的 `#adminAudioPlayer`。`playSongInAdmin` 已实现队列、格式选择与错误跳过，但缺少自定义进度条、播放/暂停按钮与音量。

前台参考：`index.html` 的 `.studio-player` + `frontend.js` 中 transport/progress/volume 事件绑定；样式在 `studio.css`。

## Goals / Non-Goals

**Goals:**

- 操作列 UI 收敛为单一「更多」入口，菜单内含编辑、播放、下载、删除。
- 编辑抽屉主表单可见「影视剧」；发行日期使用日期选择器并与 `YYYY-MM-DD` 存储格式一致。
- 后台歌曲管理页底部播放器在视觉与交互上对齐前台 Studio 播放器（两行：控件行 + 可选歌词行），保留现有播放队列与 API 逻辑。

**Non-Goals:**

- 不修改歌曲列表列定义、排序、分页或冻结列（已有独立变更）。
- 不重做编辑抽屉内原唱/作词/作曲/标签多选（见 `optimize-admin-song-edit-drawer`）。
- 不实现歌词 LRC 同步解析（歌词行可展示占位或与现有 lrc 文件名提示一致，不做新后端）。
- 不将 Studio 播放器推广到后台其他子页（艺人/标签管理等）。

## Decisions

### 1. 操作列：移除行内快捷图标，扩展 `.table-more-menu`

**选择**：删除 `edit-quick` / `play-quick` / `download-quick` 三个独立按钮的 DOM 与事件；在 `.table-more-menu` 内按顺序放置：编辑、播放（不可播时 disabled）、下载、分隔线（可选）、删除。

**理由**：与前台一致，减少操作列宽度占用，配合冻结列更整洁。

**备选**：保留播放为唯一外露图标 — 用户明确要求全部收入更多。

### 2. 发行日期：原生 `<input type="date">`

**选择**：将 `#releaseDateInput` 改为 `type="date"`；`syncReleaseDateField` 将后端值规范为 `YYYY-MM-DD`（已有 `normalizeDateInputValue` 可复用）；`releaseDateFromForm` 直接读 date input 值。

**理由**：零依赖、无障碍友好、与 ISO 日期字符串天然对齐。

**备选**：第三方 date picker — 增加体积，后台场景原生控件足够。

**边界**：历史数据中非标准日期字符串 — 打开抽屉时尽力解析为 date；无法解析则清空并允许用户重选（不阻塞保存）。

### 3. 影视剧：移出 `adm-hidden-filters` 至主表单栅格

**选择**：将 `#filmTvInput` 移到发行日期/语言同一 `adm-form-grid-2` 或独立一行，去掉 `adm-hidden-filters` 类；保存逻辑已含 `film_tv`，无需 API 变更。

### 4. 后台播放器：复用 DOM 结构与 CSS，独立 element id

**选择**：

- 在 `admin.html` 用与 `index.html` 同结构的 `.studio-player` 替换 `admin-player-compact`；audio 保留 `#adminAudioPlayer`（或 `#adminStudioAudio`）且 **无** `controls` 属性。
- CSS：在 `admin-studio.css` 中 `@import` 或复制必要 `.studio-player*` 规则，加 `.admin-app` 前缀避免污染；侧栏收起时同步 `left`（若已有 `--adm-sidebar-w` 变量则复用前台模式）。
- JS：新增 `bindAdminStudioPlayer()` — 绑定 play/pause、progress click/drag、`timeupdate` 更新 `#adminPlayerCurrentTime` / fill、volume、`ended` 委托现有 `adminNextBtn` 逻辑；`playSongInAdmin` 成功后更新 `#adminPlayerBarTitle` / `#adminPlayerBarArtist` 与播放图标。

**理由**：视觉一致、逻辑增量小，不抽取共享 bundle（避免本变更范围膨胀）。

**备选**：iframe 嵌入前台播放器 — 过度复杂。

**Non-goal 歌词行**：第二行 `#adminPlayerLyricLine` 可显示「当前暂无歌词」占位；若实现成本低可读 `.lrc` 文件名，但不作为必须项。

### 5. 主内容区底部留白

**选择**：歌曲管理主区域 `padding-bottom` 与 `.studio-player` 固定高度一致（参考前台 `studio.css` 变量），避免列表最后一行被播放器遮挡。

## Risks / Trade-offs

- **[Risk] 操作列仅更多增加一次点击** → 菜单项文案清晰（带图标），与前台一致；行点击仍可打开编辑（若现有行为保留）。
- **[Risk] `type="date"` 对历史脏数据展示为空** → 打开抽屉时 toast 或静默清空，用户可重选。
- **[Risk] 复制 studio CSS 导致双份维护** → 优先抽取共用选择器到 `studio.css` 并由 admin 页引入该 stylesheet（若 admin 已引入则只加 admin 覆盖项）。
- **[Risk] 播放器与右侧编辑抽屉 z-index 冲突** → 播放器 `z-index` 低于抽屉 overlay，与前台一致。

## Migration Plan

纯前端静态资源变更：部署后刷新 admin 页即可。无数据库迁移。回滚为还原 `admin.html` / `admin.js` / CSS 三文件。

## Open Questions

- 行点击是否仍打开编辑抽屉？（建议 **保留** 现有行点击行为，仅操作列收敛。）
- 后台播放器是否需要「播放当前列表」按钮？（建议 **保留** 等价能力：沿用当前页歌曲作为 `playQueue`，可选隐藏 📋 若与筛选语义冲突。）
