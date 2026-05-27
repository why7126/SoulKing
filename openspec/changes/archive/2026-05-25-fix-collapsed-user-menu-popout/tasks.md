## 1. 前台样式

- [x] 1.1 在 `app/static/studio.css` 为 `.front-app .app-shell.is-sidebar-collapsed .sk-user-menu` 添加收起态规则：`left: calc(100% + 8px)`、`right: auto`、`min-width: 160px`（或等效 `max-content` + min-width）
- [x] 1.2 为收起态 `.sk-user-menu-item` 添加 `white-space: nowrap`，确保中文菜单项单行显示

## 2. 后台样式

- [x] 2.1 在 `app/static/admin-studio.css` 为 `.admin-app .app-shell.is-sidebar-collapsed .adm-user-menu` 添加与前台对称的收起态定位与最小宽度规则
- [x] 2.2 为收起态 `.adm-user-menu-item` 添加 `white-space: nowrap`

## 3. 溢出与层级（按需）

- [x] 3.1 在浏览器中验证菜单向右伸出时未被侧栏或 shell 裁切；若裁切则在最小范围（如 `.sk-sidebar-bottom` / `.adm-sidebar-bottom`）设置 `overflow: visible`

## 4. 手动验收

- [x] 4.1 前台：展开侧栏 → 打开用户菜单 → 确认布局与变更前一致
- [x] 4.2 前台：收起侧栏 → 打开用户菜单 → 确认菜单在轨道右侧且「个人资料」「退出登录」等横排显示
- [x] 4.3 后台：展开/收起侧栏分别验收用户菜单，确认与前台行为一致且无竖排文字
