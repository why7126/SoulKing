## 1. DOM 结构

- [x] 1.1 将 `index.html` 中 `footer.studio-player` 重构为 `studio-player-row--controls` 与 `studio-player-row--lyrics` 两行容器
- [x] 1.2 控制行内重组：左（封面+曲名/艺人/下一首）、中（transport + 进度条与时间）、右（音量与辅助按钮）；歌词 `#playerLyricLine` 移至独立下行
- [x] 1.3 确认所有既有播放器元素 ID 不变，`frontend.js` 无需改动或仅做最小适配

## 2. 样式与高度

- [x] 2.1 在 `studio.css` 定义 `--sk-player-controls-h`、`--sk-player-lyrics-h`、`--sk-player-total-h`，重写 `.studio-player` 及子类（移除旧三列 grid）
- [x] 2.2 压缩封面、按钮、内边距与行高，使控制行约单行、歌词行约单行
- [x] 2.3 为音乐库主内容/列表区设置 `padding-bottom: var(--sk-player-total-h)`，避免末行被遮挡
- [x] 2.4 更新 `max-width` 媒体查询：窄屏允许控制行内部 wrap，歌词行始终保持独立第二行

## 3. 验证

- [x] 3.1 手动验证：播放/暂停、进度点击、音量、播放模式下拉、侧栏收起后播放器 `left` 与两行布局
- [x] 3.2 手动验证：音乐库列表滚至底部，最后一行完整可见；歌词行显示占位或同步文案
