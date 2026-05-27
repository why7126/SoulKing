## Context

前台（`index.html` + `studio.css`）与后台（`admin.html` + `admin-studio.css`）共用 Studio 底部播放器 markup：`.studio-transport` 内三个圆钮 `#prevBtn` / `#playerPlayPauseBtn` / `#nextBtn`（后台为 `admin*` 前缀）。Transport 按钮已设置固定宽高与 `display: grid; place-items: center`，但全局 `styles.css` 的 `button { padding: 9px 11px; }` 在更高层联后仍生效，挤压内容区并使 Unicode 字形视觉偏移。播放/暂停由 `frontend.js` / `admin.js` 在 `▶` 与 `⏸` 间切换 `textContent`，无额外 markup。

## Goals / Non-Goals

**Goals:**

- 圆钮**内部**的 ⏮ / ▶ / ⏭ / ⏸ 在几何上居中，前后台表现一致。
- 采用方案 A：仅 CSS 重置，不新增 SVG、不改 HTML/JS。
- 保持现有圆钮尺寸（34×34 切歌、40×40 播放）与渐变播放键样式。

**Non-Goals:**

- 不调整 transport 与进度条的整体 flex 布局。
- 不替换 Unicode 为图标字体或 SVG（方案 B）。
- 不修改播放模式、队列、歌词行等行为。

## Decisions

### 1. 方案 A：在壳样式层重置 padding 与 line-height

**选择：** 在 `.studio-transport button`（及 `[data-role="playpause"]`）上增加：

```css
padding: 0;
line-height: 1;
```

**理由：** 与现有 `grid` + `place-items: center` 配合即可消除全局 padding 干扰；改动面最小，前后台各一处规则块。

**备选（未采用）：**

- **方案 B — inline SVG：** 视觉最稳，但需改 HTML 或 JS 注入，超出本次范围。
- **方案 C — 光学 `transform`：** 需按字符分别微调，维护成本高。

### 2. 前后台对称修改

**选择：** 同时修改 `studio.css`（`.front-app .studio-transport button`）与 `admin-studio.css`（`.admin-app #adminStudioPlayer .studio-transport button`）。

**理由：** 两文件规则结构镜像；只修一侧会再现用户报告的「前台和后台播放器问题」。

### 3. 不修改全局 `styles.css` 的 button 规则

**选择：** 仅在 transport 选择器上覆盖，不动全局表单按钮 padding。

**理由：** 避免影响管理页表格、抽屉、工具栏等大量 `button` 布局。

### 4. 保留 `border-radius: 999px` 与壳内 border

Transport 规则已定义圆角与边框；重置 padding 后无需改动 `border-radius`。全局 `border-radius: 10px` 被壳规则 `999px` 覆盖，无需额外处理。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| Unicode 字形本身视觉重心仍略偏（尤其 ⏮/⏭） | 方案 A 应满足「圆内不偏」；若仍不满意，后续单独提案方案 B |
| `▶` 与 `⏸` 切换时宽度差导致轻微跳动 | 可接受；本次不改为等宽 SVG |
| 其它页面若复用 `.studio-transport` | 当前仅前台/后台播放器使用；选择器已限定 `.front-app` / `#adminStudioPlayer` |

## Migration Plan

1. 修改 `studio.css` 与 `admin-studio.css`。
2. 硬刷新或 bump 静态资源 query（`?v=`）若缓存顽固。
3. 人工目视验收前台 `index.html` 与后台 `admin.html` 播放器 transport 三钮（播放态与暂停态各看一次）。
4. 回滚：删除新增的两行 CSS 即可。

## Open Questions

（无 — 范围与方案已在 explore 阶段确认：圆钮内部偏移，方案 A。）
