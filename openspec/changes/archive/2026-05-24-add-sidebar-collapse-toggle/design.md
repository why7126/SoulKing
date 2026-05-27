## Context

前台（`index.html` + `studio.css` + `frontend.js`）与后台（`admin.html` + `admin-studio.css` + `admin.js`）均采用 `.app-shell`  flex 布局：左侧 `.app-sidebar` 固定宽约 248px（`--sk-sidebar-w` / `--adm-sidebar-w`），右侧主内容区 `flex: 1`。

当前无收起态；前台底部播放条使用 `left: var(--sk-sidebar-w)` 定位，侧栏宽度变更须同步。全局 `styles.css` 亦定义 `--app-sidebar-width: 240px`，实现时需统一折叠态变量来源，避免两套宽度不同步。

## Goals / Non-Goals

**Goals:**

- 前台、后台侧栏均支持一键收起/展开（图标按钮）
- 收起态为「图标栏」（保留 nav 图标与关键入口），展开态与现网一致
- 切换时有平滑宽度过渡；主内容区自动占满剩余宽度
- 各壳独立持久化偏好（`localStorage`），刷新后恢复
- 折叠按钮具备基本可访问性属性

**Non-Goals:**

- 移动端抽屉式侧栏或断点自动收起（本变更仅桌面壳内手动切换）
- 跨设备云端同步偏好
- 重构为 React/Vue 组件
- 修改侧栏导航项业务逻辑或路由

## Decisions

### 1. 在 `.app-shell` 上挂折叠态 class

**选择**：`.app-shell.is-sidebar-collapsed` 控制整页布局；侧栏 `aside` 本身也可加修饰 class 便于样式选择器。

**理由**：主内容区、播放条等兄弟节点可随 shell class 统一响应；与前台/后台共用 `styles.css` 中的共享规则。

**备选**：仅在 `aside` 上改 width inline style —— 播放条等外部定位元素难以联动。

### 2. 折叠宽度 64px，展开宽度保持 248px

**选择**：收起 `--*-sidebar-w: 64px`（或等价 class 覆盖）；展开维持现有 248px。

**理由**：足够容纳 36–40px 图标与内边距；与常见 icon rail 一致。

### 3. 切换按钮置于品牌区右侧

**选择**：在 `.sk-brand` / `.adm-brand` 内增加 `button.sidebar-collapse-btn`（chevron 图标），`aria-controls` 指向对应 `aside`。

**理由**：位置固定、易发现；不占用 nav 列表项。展开时 chevron 指向左（收起），收起时 chevron 指向右（展开）。

**备选**：侧栏底部独立按钮 —— 与前台底部用户区/统计挤占空间。

### 4. 收起态 UI 规则

| 区域 | 展开 | 收起 |
|------|------|------|
| 品牌标题/副标题 | 显示 | 隐藏 |
| Nav 文案 | 显示 | 隐藏，保留 SVG 图标 |
| Nav 项 | 左对齐 icon+文字 | 居中 icon，`title` 保留 |
| 前台统计行 | 显示 | 隐藏 |
| 前台/后台用户名 | 显示 | 隐藏，保留头像按钮 |
| 用户菜单 | 行为不变 | 仍从头像弹出 |

过渡：`transition: width 0.2s ease`；文案 `opacity` + `overflow: hidden` 避免截断闪烁。

### 5. 状态持久化键

**选择**：

- 前台：`localStorage` key `pm.sidebarCollapsed.front`（值 `"1"` / `"0"`）
- 后台：`pm.sidebarCollapsed.admin`

**理由**：键名带项目前缀，前后台独立；字符串便于调试。

**备选**：`sessionStorage` —— 刷新丢失，不符合「记住偏好」。

### 6. 脚本职责分离

**选择**：`frontend.js` 初始化 `initFrontSidebarCollapse()`；`admin.js` 初始化 `initAdminSidebarCollapse()`。共享逻辑可提取为同文件内小函数（读/写 storage、toggle class），不新建独立 bundle。

**理由**：两壳已是独立模块入口，避免 `app.js` 等未挂载脚本。

### 7. CSS 变量联动播放条

**选择**：折叠态下在 `.front-app.app-shell.is-sidebar-collapsed`（或 `.front-app .app-shell.is-sidebar-collapsed`）覆盖 `--sk-sidebar-w: 64px`；播放条继续 `left: var(--sk-sidebar-w)` 并加 `transition` 与侧栏同步。

**理由**：最小改动现有定位公式。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| `styles.css` 240px 与 studio 248px 不一致 | 折叠态仅在 studio/admin-studio 覆盖壳内变量；共享选择器一并更新 |
| 收起态用户菜单向上弹出被裁切 | `.sk-sidebar-bottom` / `.adm-sidebar-bottom` 收起时仍 `overflow: visible` |
| 折叠时 nav 文字瞬间消失难以扫读 | 保留 `title`；图标居中 |
| localStorage 不可用（隐私模式） | 捕获异常，降级为 session 内默认展开 |
| 宽表/固定层动画卡顿 | 过渡 200ms，仅 width/left，避免 layout thrashing 属性 |

## Migration Plan

1. 部署 HTML/CSS/JS 更新，递增 `?v=`。
2. 首次访问默认展开；用户切换后写入 storage。
3. 回滚：移除 toggle 按钮与 class 逻辑，删除 storage 读取即可恢复常展侧栏。

## Open Questions

（无 —— 首版不实现窄屏自动收起；若后续需要可单独 change。）
