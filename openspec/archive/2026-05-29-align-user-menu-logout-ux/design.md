## Context

前台（`index.html` + `studio.css` + `frontend.js`）与后台（`admin.html` + `admin-studio.css` + `admin.js`）侧栏用户菜单已具备 Studio/Admin 危险项样式（`user-menu-item--destructive`、顶部分隔、`--sk-danger` / `--adm-danger`）及 `confirmLogout()` 流程（关菜单 → 确认 → `POST /auth/logout` → `/login`）。

当前断裂点在于确认步骤仍调用全局 `openModal` / `#modalOverlay`（`styles.css` Hermes 灰阶），与个人资料、修改密码使用的 `sk-self-service-overlay` + `sk-modal-card`（前台 Studio 皮肤）不一致。`ui-design.md` 已记录该差异并标记为待统一项。

约束：不修改 `sidebar-user-menu-popout` 定位契约；不改变其它业务确认（歌单删除、批量删除等）对 `#modalOverlay` 的既有用法（本变更仅退出登录）。

## Goals / Non-Goals

**Goals:**

- 为前后台各增加专用「退出登录确认」弹层，视觉与各自壳设计令牌一致（前台复用 `sk-self-service-overlay` / `sk-modal-*` 结构；后台使用 `adm-*` 对称组件）。
- `confirmLogout()` 仅操作专用 overlay，不再调用 `openModal`。
- 确认按钮呈现危险语义（危险色或 `btn-*-danger` 等价 class）；取消为次要按钮；支持 Esc / 遮罩点击 / 关闭按钮取消（与个人资料弹层行为对齐）。
- 保持现有登出 API 与跳转逻辑；用户菜单危险项与分隔样式经回归验收仍满足主 spec。

**Non-Goals:**

- 将全站 `#modalOverlay` 统一为 Studio（歌单、歌曲删除等仍可用 Hermes 模态）。
- 修改登录页、个人资料/改密码表单逻辑。
- 改动菜单 HTML 的 `role="menu"` 语义或收起态弹出规则。

## Decisions

### 1. 专用 overlay DOM，而非扩展 `openModal`

**选择**：在 `index.html` / `admin.html` 各增加 `#logoutConfirmOverlay`（class：`sk-self-service-overlay` 前台 / 后台等价 `adm-self-service-overlay` 或复用已有 overlay 模式），内含标题、说明文案、取消与确认按钮。

**理由**：DOM 与样式可与 `profileOverlay` 并列维护；避免为单一流程改造通用 `openModal` 的 Hermes 结构。

**备选**：给 `#modalOverlay` 增加 Studio 主题 class — 会影响所有 `openModal` 调用，范围过大。

### 2. 前台复用 `sk-self-service-overlay` 样式块

**选择**：新 overlay 使用与 `#profileOverlay` 相同的容器与卡片 class（`sk-self-service-overlay`、`sk-modal-card`、`sk-modal-head`、`sk-modal-actions`）；确认按钮新增 `btn-studio-danger`（或在 `studio.css` 定义 `.btn-studio-danger` 映射 `--sk-danger` 边框/字色/hover）。

**理由**：零新增布局模式；与 `ui-design.md` §2 自助表单一致。

**备选**：内联样式 — 不利于维护。

### 3. 后台 Admin 对称实现

**选择**：后台新增结构对称的 overlay（`adm-self-service-overlay` + `adm-modal-card`，若已有 partial 则复用）；按钮 `btn-adm-secondary` + `btn-adm-danger`（或等价）。

**理由**：后台无 `sk-*`；须用 `--adm-*` 令牌，避免在前台 CSS 中混用。

### 4. `confirmLogout()` 流程

**选择**（前后台对称）：

1. `set*UserMenuOpen(false)`
2. 显示 `#logoutConfirmOverlay`，聚焦确认按钮（可选）
3. 用户确认 → `POST /auth/logout`（失败仍跳转 `/login`）→ `location.href = '/login'`
4. 用户取消 / 遮罩 / Esc → 隐藏 overlay，无 API 调用

**理由**：与现网 `confirmLogout` 副作用一致，仅替换 UI 载体。

### 5. 用户菜单样式：验收为主，无结构性改动

**选择**：若代码已含 `user-menu-item--destructive` 与 `border-top` 分隔，实现阶段以目视回归为主；spec 保留既有 MUST 条款。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 两套确认 overlay 增加 DOM | 仅退出登录一项，体量小；与 profile/password 模式一致 |
| 后台缺少 `btn-adm-danger` | 在 `admin-studio.css` 最小新增一条规则 |
| z-index 与 profile/password 同时打开 | 退出前先关用户菜单；overlay z-index 与 `sk-self-service-overlay` 同级（80） |
| 未来全站模态统一时需再迁移 | spec 注明仅退出登录专用；全站统一为后续变更 |

## Migration Plan

1. 先加 HTML + CSS，再在 JS 中切换 `confirmLogout` 实现，便于对比截图。
2. 无数据迁移；静态资源部署即可。
3. 回滚：还原四个静态文件与 spec delta。

## Open Questions

（无 — 用户诉求为登出 UI/UE 与 Studio 整体一致；确认弹层 Studio 化即为范围。）
