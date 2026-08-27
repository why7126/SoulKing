## 1. 前台 CSS

- [x] 1.1 在 `app/static/studio.css` 的 `.front-app .studio-transport button` 规则中增加 `padding: 0` 与 `line-height: 1`
- [x] 1.2 确认 `[data-role="playpause"]` 继承同一重置（无需重复规则块，除非被其它选择器覆盖）

## 2. 后台 CSS

- [x] 2.1 在 `app/static/admin-studio.css` 的 `.admin-app #adminStudioPlayer .studio-transport button` 规则中增加相同的 `padding: 0` 与 `line-height: 1`
- [x] 2.2 确认后台播放/暂停圆钮在 ▶ 与 ⏸ 切换后仍居中

## 3. 验收

- [x] 3.1 前台：打开音乐库页，目视检查 transport 三钮（播放中与暂停各一次）
- [x] 3.2 后台：在歌曲管理页播放曲目，目视检查 `#adminStudioPlayer` transport 三钮
- [x] 3.3 窄视口（≤900px）快速扫一眼，确认换行后圆钮内图标仍不偏
