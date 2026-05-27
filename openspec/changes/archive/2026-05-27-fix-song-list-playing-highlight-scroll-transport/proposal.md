## Why

前台在上一首/下一首后虽会给当前播放行加 `is-active`，但列表滚动将行顶对齐到滚动容器顶部，未扣除 sticky 表头高度，导致高亮行被「字段行」（表头）遮挡；后台播放仅更新 `currentPlayIndex`，列表仍按 `activeSongId`（编辑选中）高亮，切歌后无「正在播放」行态。另：曲库分页下播放队列与当前页可能不一致，切歌到不在当前页的歌曲时列表无法反映播放位置。播放器 transport 圆钮内图标偏位若仍存在，应对齐既有壳层规格。

## What Changes

- **前台音乐库与歌单详情**：滚动当前播放行进入可视区时，采用**方案 A**：在计算 `scrollTop` 时减去列表滚动容器内 `thead` 高度（及必要时的少量间距），避免 sticky 表头盖住播放行；歌单详情列表（`playlistDetailSongList` / `.pd-table-wrap`）与曲库共用同一套逻辑并验收。
- **跨页**：当前播放索引对应歌曲不在当前已加载页时，自动将 `songPage`（前台）或 `songPage`（后台）跳到包含该曲的页并重新拉取列表，再应用高亮与滚动。
- **后台**：区分「正在播放」与「编辑选中」行样式：播放态视觉与前台 `tr.is-active`（含冻结列 td 背景）**语义一致、token/对比度同级**；编辑选中使用较弱态（可沿用或微调现有 `is-active` 编辑语义，或改名为 `is-selected` 等，以设计为准）。播放/切歌/自然播放结束时 MUST 更新播放行高亮并在 `.adm-table-scroll` 内滚动至可见（同样扣除表头高度）。
- **Transport 圆钮**：若代码尚未满足 `openspec/specs/web-static-client-shells/spec.md` 中「Studio 播放器 transport 圆钮图标居中」要求，则按该条落实 CSS（覆盖全局 `button` padding、`grid` 居中等）；若已满足，本变更任务中仅做回归确认。

## Capabilities

### New Capabilities

（无；行为均归属既有壳层能力。）

### Modified Capabilities

- `web-static-client-shells`：增量补充「当前播放行在列表中的高亮、可见滚动、跨页同步」及后台「播放态与编辑态行样式分离且与前台播放态一致」的可验收需求；transport 居中以基线 spec 为准，本变更仅跟踪实现或验收。

## Impact

- 静态脚本：`app/static/frontend.js`、`app/static/admin.js`
- 样式：`app/static/studio.css`、`app/static/admin-studio.css`（及必要时与 `styles.css` 中 `button` 冲突的覆盖）
- 不修改服务端 API 契约；仅客户端分页参数与列表重载行为变化。
