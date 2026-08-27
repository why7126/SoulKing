## Why

前台与后台 Studio 底部播放器的 transport 圆钮（上一首、播放/暂停、下一首）内，Unicode 图标（⏮ / ▶ / ⏭ / ⏸）在视觉上明显偏离圆心。根因是全局 `styles.css` 为所有 `button` 设置了 `padding: 9px 11px`，而 `studio.css` / `admin-studio.css` 虽用 `display: grid; place-items: center` 固定了圆钮尺寸，却未重置 padding，导致字形在极小且不对称的内容区内偏移。该问题影响日常播放操作的可读性与品质感，应在不改交互逻辑的前提下快速修复。

## What Changes

- 在前台 `studio.css` 的 `.studio-transport button` 规则中采用**方案 A（最小 CSS）**：`padding: 0`、`line-height: 1`，保留现有 `grid` 居中与圆钮尺寸。
- 在后台 `admin-studio.css` 的 `#adminStudioPlayer .studio-transport button` 上应用相同重置，保证前后台一致。
- 播放/暂停按钮在 `▶` 与 `⏸` 切换时，图标 MUST 仍在圆钮内几何居中（不引入 SVG 或大改 markup）。
- 不修改播放逻辑、播放模式、进度条或音量行为。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：为前台与后台 Studio 底部播放器 transport 圆钮增加图标居中的可验收要求。

## Impact

- `app/static/studio.css` — `.front-app .studio-transport button` 及 `[data-role="playpause"]`
- `app/static/admin-studio.css` — `.admin-app #adminStudioPlayer .studio-transport button` 及 `[data-role="playpause"]`
- 依赖链：`index.html` / `admin.html` 均先加载 `styles.css`，再加载各壳样式；修复仅在壳样式层覆盖全局 button padding
- 无 API、数据库或 JavaScript 变更
