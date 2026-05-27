## Context

前台 Studio 壳（`index.html` + `frontend.js` + `studio.css`）采用左侧主导航 + 顶栏搜索/操作 + 主内容区布局。当前侧栏包含：

- **音乐**：音乐库（可用）、歌单（脚本已实现完整歌单空间，但产品要求暂时从导航关闭）、艺人（toast 占位）、专辑（toast 占位）
- **媒体**：图片、视频（HTML 已 `disabled`，但缺少 `.sk-nav-item.is-disabled` 样式）
- **系统**：设置、关于（需删除）
- **底部**：头像 + 硬编码用户名「SoulKing」+ 四项下拉菜单（仅头像可点击）

顶栏右侧有纯占位通知铃铛（无 JS 绑定）。

后台壳（`admin.html`）已有 `adm-user-row` / `adm-user-menu` 模式，可作为用户菜单交互参考。

## Goals / Non-Goals

**Goals:**

- 顶栏不再展示通知入口。
- 侧栏移除「系统」分组；底部用户区整行可展开菜单（个人资料、修改密码、进入后台、退出登录）。
- 歌单、艺人、图片、视频在侧栏统一 disabled 置灰，视觉与 `sk-tier-btn.is-disabled` 一致。
- 音乐库、专辑保持当前可用/占位行为；默认 landing 仍为音乐库。
- 递增静态资源 `?v=` 缓存版本。

**Non-Goals:**

- 实现个人资料、修改密码、退出登录的真实认证 API。
- 删除歌单相关 DOM/脚本（`#playlistRoutesWrap` 等保留，仅关闭侧栏入口）。
- 专辑置灰（用户未要求）。
- 动态用户名/头像 URL（继续硬编码或占位，除非已有接口可零成本接入）。

## Decisions

### 1. 用户行：整行 `<button>` 包裹头像与用户名

**选择**：将 `sk-user-row` 改为单一 `button#frontUserMenuBtn`（或等价），内含头像装饰元素与 `sk-user-meta`；移除仅头像独立的 click 监听，统一 `setFrontUserMenuOpen`；保留 `aria-expanded` / `aria-controls` / `role="menu"` 无障碍属性。

**理由**：符合用户「点击头像+名称出现菜单」的预期；与后台侧栏模式对齐。

**备选**：分别给头像和用户名绑定同一 handler —— 可行但 DOM 更碎，不采用。

### 2. 未实现导航：HTML `disabled` + CSS `is-disabled`

**选择**：对歌单、艺人、图片、视频按钮添加 `disabled`、`class="sk-nav-item is-disabled"`、`title="暂未开发"`；在 `studio.css` 新增：

```css
.front-app .sk-nav-item:disabled,
.front-app .sk-nav-item.is-disabled {
  opacity: 0.38;
  cursor: not-allowed;
  pointer-events: none;
}
```

**理由**：与已有 `sk-tier-btn.is-disabled` 令牌一致；`pointer-events: none` 防止误触。

**备选**：保留可点击并 toast —— 与用户明确要求「置灰」冲突，不采用。

### 3. 歌单导航关闭但代码保留

**选择**：侧栏歌单按钮 disabled；`frontend.js` 中 `[data-sk-nav="playlists"]` 点击分支保留但不可达；`syncNavForPlaylistState` 移除对 `settings`/`about` 的引用；若 `state.mainNav === "playlists"` 的遗留状态，初始化时强制 `library`。

**理由**：产品要求导航收敛；避免大删歌单模块增加回归成本；后续单独 change 可重新 `enabled`。

### 4. 顶栏通知删除与 flex 收尾

**选择**：删除 `.studio-header-notify` 按钮；若顶栏最后一项 `margin-left: auto` 失效，将 `auto` 迁移到搜索框容器或歌单操作区（视当前 DOM 结构微调）。

**理由**：纯 UI 删除，无行为影响。

### 5. 菜单项行为不变

**选择**：个人资料/修改密码/退出登录继续 toast 占位；进入后台继续 `window.location.href = "/admin"`。

**理由**：本变更聚焦布局与导航，不扩展认证能力。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 歌单功能已有实现但导航不可达 | 代码保留；文档与 spec 注明；后续 change 可恢复 |
| 用户误以为专辑也可用 | 专辑仍 toast「即将推出」，与音乐库形成对比 |
| 硬编码用户名与真实账户不一致 | Non-Goal；后续 auth change 再接 API |
| disabled 按钮仍被 JS 查询选中 | `querySelectorAll("[data-sk-nav]")` 仅绑定未 disabled 项，或 handler 内 early return |

## Migration Plan

1. 部署更新后的 `index.html`、`frontend.js`、`studio.css`（递增 `?v=`）。
2. 用户硬刷新前台页，按 tasks 验收侧栏与顶栏。
3. 回滚：恢复三文件上一版本即可，无数据迁移。

## Open Questions

（无 — 探索阶段已确认：歌单按用户字面要求置灰；专辑保持现状。）
