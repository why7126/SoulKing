## 1. HTML 结构调整（index.html）

- [x] 1.1 删除顶栏 `.studio-header-notify` 通知铃铛按钮
- [x] 1.2 删除侧栏「系统」分组及「设置」「关于」按钮
- [x] 1.3 将歌单、艺人按钮改为 `disabled` + `is-disabled` + `title="暂未开发"`（移除或保留 `data-sk-nav` 但不可激活）
- [x] 1.4 确认图片、视频已 disabled 且带 `is-disabled`
- [x] 1.5 重构底部用户区：整行可点击按钮包裹头像与用户名称；保留下拉菜单四项 DOM 与 ARIA 属性
- [x] 1.6 递增 `index.html` 引用的 `styles.css` / `studio.css` / `frontend.js` 的 `?v=` 版本号

## 2. 样式（studio.css）

- [x] 2.1 新增 `.front-app .sk-nav-item:disabled` / `.is-disabled` 置灰规则（opacity、cursor、pointer-events），与 `sk-tier-btn.is-disabled` 一致
- [x] 2.2 调整 `.sk-user-row` / 新用户触发按钮的 hover、focus、`aria-expanded` 视觉态
- [x] 2.3 删除或清理 `.studio-header-notify` 及相关顶栏 flex 规则；确保搜索/操作区布局正常
- [x] 2.4 递增 `studio.css` 自身引用版本（若 HTML 已统一 bump 则确认一致）

## 3. 脚本逻辑（frontend.js）

- [x] 3.1 将用户菜单开关绑定到整行触发按钮；更新 `els` 引用与 `setFrontUserMenuOpen`
- [x] 3.2 保留个人资料/修改密码/退出登录 toast 占位；「进入后台」跳转 `/admin`
- [x] 3.3 清理 `syncNavForPlaylistState` 中对 `settings`/`about` 的引用
- [x] 3.4 确保 `[data-sk-nav]` 点击处理不作用于 disabled 项；初始化时 `mainNav` 为 `library`
- [x] 3.5 保留 document 级 click-outside 关闭用户菜单逻辑
- [x] 3.6 递增 `frontend.js` 引用版本（若 HTML 已统一 bump 则确认一致）

## 4. 验收

- [x] 4.1 顶栏无通知铃铛；侧栏无系统分组
- [x] 4.2 歌单、艺人、图片、视频置灰且不可切换主视图；音乐库与专辑行为符合预期
- [x] 4.3 点击侧栏底部头像或用户名可展开/关闭四项菜单；「进入后台」可跳转 `/admin`
- [x] 4.4 点击页面其他区域关闭用户菜单
