## Context

前台底部播放器（`index.html` 中 `footer.studio-player`）当前结构：

- 外层：`display: grid; grid-template-columns: 左 | 中 | 右` 三列。
- **左列**：52×52 封面 + 曲名/艺人/「下一首」三行文本。
- **中列**（`flex-direction: column`）：transport（上一首/播放/下一首/模式下拉）→ 进度条行 → 歌词 `<p>`，纵向 `gap: 8px`，是高度膨胀主因。
- **右列**：音量、播放列表、词/全屏辅助按钮。

播放器 `position: fixed; bottom: 0`，`left` 随侧栏宽度过渡（已有规范）。`frontend.js` 通过 `#playerBarTitle`、`#playerPlayPauseBtn`、`#playerLyricLine` 等 ID 更新 UI，播放逻辑无需改动。

## Goals / Non-Goals

**Goals:**

- 播放器视觉与 DOM 语义为 **两行**：上行 = 现有全部控制能力；下行 = 歌词单行。
- 总高度明显低于当前（参考：上行约 48–56px 内容高 + 下行约 24–28px + 紧凑 padding）。
- 列表主区域底部预留与播放器新高度一致，最后一行不被遮挡。
- 侧栏收起/展开时播放器 `left` 与歌词行宽度行为不变。

**Non-Goals:**

- 实现 LRC 同步滚动、歌词面板、全屏播放器。
- 修改播放队列、`playMode`、API。
- 后台 admin 播放器（`.admin-player-compact`）布局。
- 移除「词」「全屏」等未实现辅助按钮（保持现状）。

## Decisions

### 1. DOM：两行容器替代三列网格

**选择**：将 `footer.studio-player` 改为两层：

```html
<footer class="studio-player panel">
  <div class="studio-player-row studio-player-row--controls">…</div>
  <div class="studio-player-row studio-player-row--lyrics">
    <p class="studio-lyric-hint" id="playerLyricLine">…</p>
  </div>
  <audio id="audioPlayer" …></audio>
</footer>
```

- **上行**（`--controls`）：内部仍用横向 flex/grid，从左到右：左区（封面 + 曲名/艺人，「下一首」可并入单行或副标题省略）、中区（transport + 进度条同一行或紧邻不换行）、右区（音量 + 辅助按钮）。
- **下行**（`--lyrics`）：仅 `#playerLyricLine`，全宽居中或左对齐，单行 `ellipsis`。

**理由**：满足产品「只有 2 行内容」的明确结构；歌词与控件解耦，避免中列三叠。

**替代方案**：保留三列、仅缩小字号 — 无法消除中列三行堆叠，否决。

### 2. 上行布局：控件单行优先

**选择**：`studio-player-row--controls` 使用 `display: flex; align-items: center; gap: 12px; min-height: 48px`。

- 封面缩至 **40×40**（或 36×36）。
- 曲名/艺人合并为两行以内（`.t` + `.a`），`#playerNextHint` 改为单行小字，与艺人同一 meta 块或 hover title，避免左区过高。
- transport 与 `studio-progress-row` 置于 **同一 flex 子组**（`studio-player-transport-block`），在宽屏下横向排列：按钮组 | 当前时间 | 进度条 | 总时长。
- 播放模式下拉高度与 transport 按钮对齐（约 32px）。

**理由**：上行一条视觉基线，高度由最高控件（播放钮 ~40px）决定，而非三行相加。

### 3. 样式 token：统一播放器高度变量

**选择**：在 `:root` 或 `.front-app` 增加：

- `--sk-player-controls-h`（上行最小高度，如 52px）
- `--sk-player-lyrics-h`（下行，如 26px）
- `--sk-player-total-h`：二者 + 垂直 padding（如 8+8）

主内容滚动区（如 `.studio-library-list` 或 `.studio-main-column`）`padding-bottom: var(--sk-player-total-h)`，替代隐式留白。

**理由**：侧栏动画与后续微调只需改变量。

### 4. 响应式：保持两行语义

**选择**：

- `max-width: 1100px`：上行允许 **内部** wrap（如右区换到第二 flex 行），但 **不得** 把歌词塞回上行；下行歌词始终独立。
- 极窄屏可隐藏「下一首」文案或辅助按钮，仍保留 transport + 进度 + 音量核心。

**理由**：与 proposal 中「不得恢复三行以上纵向堆叠」一致。

### 5. JavaScript：最小改动

**选择**：保留现有元素 ID；若仅移动 DOM 节点，**不修改** `frontend.js`。若合并 meta 结构，确保 `#playerBarTitle`、`#playerBarArtist`、`#playerNextHint` 等查询仍有效。

**理由**：降低回归风险。

## Risks / Trade-offs

- **[Risk] 窄屏上行换行导致高度略高于单行** → 限制 wrap 为一次，并 cap `max-height`；辅助按钮 `display: none` 于 `<900px`。
- **[Risk] 进度条与 transport 挤在同一行可读性下降** → 进度条 `flex: 1; min-width: 120px`；transport 按钮略缩小（40px 播放钮）。
- **[Risk] 列表底部 padding 不足仍遮挡** → 用 `--sk-player-total-h` 实测 footer 实际高度并同步。
- **[Trade-off] 「下一首」提示与艺人争空间** → 优先保证曲名/艺人；下一首可缩短为图标或 title 属性。

## Migration Plan

1. 调整 `index.html` 播放器 DOM 为两行结构。
2. 重写 `studio.css` 中 `.studio-player` 及相关规则，删除旧三列 grid 规则。
3. 设置 `--sk-player-*` 并更新主栏 `padding-bottom`。
4. 浏览器手动验证：播放/暂停、进度拖拽、音量、模式下拉、侧栏收起、音乐库列表末行可见性。

无数据迁移；静态资源发布即生效。

## Open Questions

- 「下一首」提示是否保留为可见第三行文本，或收起到 tooltip（默认：单行小字，过长 ellipsis）。
- 歌词行左对齐还是居中（默认：居中，与现 `studio-lyric-hint` 一致）。
