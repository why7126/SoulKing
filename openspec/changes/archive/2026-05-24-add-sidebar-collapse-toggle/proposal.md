## Why

前台与后台壳当前左侧导航栏固定约 248px 宽，在小屏或需要更大主内容区时占用较多横向空间。用户希望在两个壳中都能通过点击图标收起/展开侧栏，在保留导航可达性的同时让主内容区获得更多可视面积。

## What Changes

- **前台壳侧栏收起/展开**：在 `.sk-studio-sidebar` 增加折叠切换控件（图标按钮）；收起时缩为仅图标窄栏，展开时恢复当前完整宽度与文案。
- **后台壳侧栏收起/展开**：在 `.adm-sidebar` 采用相同交互模式，视觉与前台一致。
- **状态持久化**：各壳独立将收起/展开偏好写入 `localStorage`，刷新或再次进入同壳时恢复上次状态。
- **布局联动**：主内容区、依赖侧栏宽度的固定层（如前台底部播放条）随侧栏宽度平滑过渡。
- **可访问性**：切换按钮提供 `aria-label`、`aria-expanded`；收起态导航项保留 `title` 或等价 tooltip 以识别菜单含义。
- 递增 `styles.css` / `studio.css` / `admin-studio.css` 及对应 HTML 脚本引用中的 `?v=` 缓存版本。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：新增前台壳与后台壳侧栏可收起/展开的行为与验收要求；补充收起态下导航、品牌区与用户区（前台）的展示约束。

## Impact

- **前端 HTML**：`app/static/index.html`、`app/static/admin.html`（折叠切换按钮 DOM）。
- **前端 CSS**：`app/static/styles.css`（共享 `--app-sidebar-width` 与 `.app-shell` 折叠态）、`app/static/studio.css`、`app/static/admin-studio.css`（壳内品牌/导航/底部用户区收起样式）。
- **前端 JS**：`app/static/frontend.js`、`app/static/admin.js`（切换逻辑、`localStorage` 读写、初始化时应用状态）。
- **后端 / API**：无变更。
