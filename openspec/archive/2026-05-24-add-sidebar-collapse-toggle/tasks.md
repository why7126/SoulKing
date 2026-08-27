## 1. 共享样式与布局变量（styles.css）

- [x] 1.1 定义折叠态宽度常量（如 `--sidebar-w-collapsed: 64px`）及 `.app-shell.is-sidebar-collapsed` 基础规则
- [x] 1.2 统一 `--app-sidebar-width` 与壳内 `--sk-sidebar-w` / `--adm-sidebar-w` 在折叠/展开下的覆盖方式
- [x] 1.3 为侧栏 width 与依赖侧栏宽度的固定层添加 `transition`（200ms ease）

## 2. 前台壳（index.html + studio.css + frontend.js）

- [x] 2.1 在 `.sk-brand` 增加 `#frontSidebarCollapseBtn`（chevron 图标，`aria-label` / `aria-expanded` / `aria-controls`）
- [x] 2.2 `studio.css`：收起态隐藏品牌文案、nav 文字、统计行、用户名；nav 图标居中；底部用户区保留头像
- [x] 2.3 `studio.css`：折叠态覆盖 `--sk-sidebar-w`；播放条 `left` 随变量联动
- [x] 2.4 `frontend.js`：实现 `initFrontSidebarCollapse()` — toggle `.app-shell.is-sidebar-collapsed`、更新 `aria-expanded`、读写 `localStorage` key `pm.sidebarCollapsed.front`
- [x] 2.5 页面加载时（DOMContentLoaded / 模块初始化）应用已存偏好，默认展开
- [x] 2.6 递增 `index.html` 中 `studio.css` / `frontend.js` 的 `?v=`

## 3. 后台壳（admin.html + admin-studio.css + admin.js）

- [x] 3.1 在 `.adm-brand` 增加 `#adminSidebarCollapseBtn`（与前台一致的折叠图标按钮）
- [x] 3.2 `admin-studio.css`：收起态样式（品牌/nav 文字隐藏、图标居中、底部头像保留）
- [x] 3.3 `admin.js`：实现 `initAdminSidebarCollapse()`，storage key `pm.sidebarCollapsed.admin`
- [x] 3.4 递增 `admin.html` 中 `admin-studio.css` / `admin.js` 的 `?v=`

## 4. 验收

- [x] 4.1 前台：展开 ↔ 收起切换流畅，主内容区与播放条宽度同步
- [x] 4.2 前台：收起态可点击音乐库等 nav 图标；头像菜单仍可用
- [x] 4.3 前台：刷新后保持上次收起/展开状态
- [x] 4.4 后台：展开 ↔ 收起切换流畅，主内容区宽度同步
- [x] 4.5 后台：收起态 nav 与用户菜单仍可用；刷新后恢复偏好
- [x] 4.6 前台与后台侧栏偏好互不影响
