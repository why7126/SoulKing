## 1. 布局归位（index.html + studio.css）

- [x] 1.1 将用户区从顶栏 `.studio-header-end` 移除（删除 `sk-header-user-wrap`）
- [x] 1.2 在 `.sk-sidebar-bottom` 内恢复用户区：统计行 + `.sk-user-row`（`#frontUserMenuBtn.sk-user-avatar` + `.sk-user-meta`）+ `#frontUserMenu`
- [x] 1.3 菜单向上弹出：`bottom: calc(100% + 6px)`，`.sk-sidebar-bottom { position: relative }`（对齐后台 `adm-user-menu`）
- [x] 1.4 递增 `index.html` 中 `studio.css` 的 `?v=`（当前 v19）

## 2. 脚本修复（frontend.js）

- [x] 2.1 `setFrontUserMenuOpen(true)` 设置 `frontUserMenuInteractAfter = performance.now() + 350`
- [x] 2.2 打开后菜单 `pointer-events: none`，双 `requestAnimationFrame` 后恢复
- [x] 2.3 `handleFrontUserMenuItem`：菜单 hidden 或冷却期内 return；否则关闭并执行 action
- [x] 2.4 菜单项 listener 经 `handleFrontUserMenuItem` 包装，保留 `stopPropagation()`
- [x] 2.5 `#frontUserMenuBtn` click：`stopPropagation()` + toggle `hidden`
- [x] 2.6 document `click`：菜单已展开且 target 不在 `#frontUserMenu` / `#frontUserMenuBtn` 内时关闭
- [x] 2.7 递增 `index.html` 中 `frontend.js` 的 `?v=`（当前 v40）

## 3. 已尝试但未采用的方案（记录）

- [x] 3.1 `ignoreNextOutsideClick` + `closest(".sk-sidebar-bottom")` —— 已替换为 2.x 方案
- [x] 3.2 顶栏用户区对照实验 —— 闪退仍复现，已回滚至侧栏底部

## 4. 验收

- [x] 4.1 单击侧栏底部 **头像按钮**：菜单展开且持续可见，不会一闪消失
- [x] 4.2 可依次点击「个人资料」「修改密码」「进入后台」「退出登录」
- [x] 4.3 点击主内容区或侧栏导航项后菜单关闭；点击「首歌库」统计行亦应关闭已展开菜单
- [x] 4.4 再次点击头像可 toggle 关闭菜单
- [x] 4.5 顶栏右侧不存在用户头像或用户菜单入口
