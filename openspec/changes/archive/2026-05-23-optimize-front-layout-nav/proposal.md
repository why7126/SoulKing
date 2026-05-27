## Why

前台 Studio 壳（`index.html`）侧栏与顶栏仍保留占位或未收敛的导航元素：顶栏通知铃铛无实际功能；侧栏「系统」分组（设置、关于）与产品当前范围不符；底部用户区虽已存在但仅头像可点开菜单；部分未上线模块（歌单、艺人、图片、视频）在视觉上未统一置灰，易让用户误以为可进入。需在一轮变更中收敛前台壳导航与用户信息入口，使可用入口清晰、占位入口一致。

## What Changes

- **删除顶栏通知**：移除 `studio-top-header` 内通知铃铛按钮及关联样式（`.studio-header-notify`）。
- **删除侧栏「系统」分组**：移除「设置」「关于」菜单项及对应导航逻辑引用。
- **完善底部用户区**：侧栏底部保留/强化「头像 + 用户名称」一行；**整行**可点击展开向上弹出的下拉菜单，包含：个人资料、修改密码、进入后台、退出登录（后两项沿用现有跳转/占位 toast 行为）。
- **未实现导航项置灰**：歌单、艺人、图片、视频在侧栏以 disabled + `is-disabled` 呈现，不可点击，悬停显示「暂未开发」提示；补充 `.sk-nav-item.is-disabled` 视觉样式与 `sk-tier-btn` 一致。
- **专辑菜单**：保持当前可点击 + toast「该模块即将推出」行为（用户未要求置灰）。
- 递增 `index.html` / `frontend.js` / `studio.css` 静态资源 `?v=` 缓存版本。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：新增/强化前台壳侧栏导航结构、未实现项禁用态、底部用户菜单与顶栏精简的验收场景。

## Impact

- **前端**：`app/static/index.html`（侧栏 DOM、删除顶栏通知与系统分组）、`app/static/studio.css`（导航 disabled 态、用户行可点击样式、顶栏 flex）、`app/static/frontend.js`（用户整行菜单切换、移除 settings/about/playlists/artists 导航激活逻辑、歌单 nav 不再从侧栏可达）。
- **后端 / API**：无变更。
- **行为说明**：歌单相关页面与脚本逻辑保留在代码库中，但侧栏入口关闭直至后续单独变更重新开放；用户仍可通过「进入后台」访问管理功能。
