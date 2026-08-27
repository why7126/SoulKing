## Why

侧栏用户菜单已采用 SoulKing Studio 视觉（`sk-user-menu` / `adm-user-menu`、危险项 `user-menu-item--destructive`、顶部分隔），但用户点击「退出登录」后弹出的确认框仍走全局 Hermes `#modalOverlay`（`styles.css` 灰阶 `--panel`），与个人资料、修改密码等 Studio 弹层（`sk-self-service-overlay`）及壳内主界面不一致，造成「菜单是 Studio、确认框是旧全局模态」的断裂感。需要在不改动菜单定位契约的前提下，将退出登录的确认交互与危险操作视觉统一到各壳设计体系，并写入 spec 防止再次混用 Hermes 模态。

## What Changes

- 为前后台壳新增专用的「退出登录」确认弹层（Studio / Admin 皮肤），替代 `confirmLogout()` 对 `#modalOverlay` / `openModal` 的调用；结构对齐现有 `sk-self-service-overlay` / `sk-modal-card`（前台）与后台等价 Admin 组件（`adm-modal-card` 或复用已有 Admin 面板令牌）。
- 确认弹层使用各壳危险色语义：标题/文案层级、`btn-studio-secondary` + 危险主按钮（或 `btn-adm-*` 对称）；取消关闭弹层且不调用登出 API；确认后执行 `POST /auth/logout` 并导航至 `/login`（与现网认证行为一致）。
- 校验并补齐用户菜单侧：前后台「退出登录」项 MUST 保留 `user-menu-item--destructive`、顶部分隔线与 `--sk-danger` / `--adm-danger` hover；后台 MUST NOT 再依赖 `:last-child` 着色。
- 更新 `web-static-client-shells` delta spec：明确退出确认弹层的 Studio/Admin 视觉、按钮语义与 API 登出流程的验收场景；注明退出确认 **不得** 再使用 Hermes 全局 `#modalOverlay`（其它批量操作确认可暂不改）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充/收紧前台与后台壳「退出登录」确认弹层须使用各壳 Studio/Admin 皮肤（非 Hermes `#modalOverlay`），并与用户菜单危险项样式、分隔、真实登出 API 流程的验收场景对齐。

## Impact

- `app/static/index.html` — 新增前台退出确认 overlay DOM（若尚不存在）
- `app/static/admin.html` — 新增后台退出确认 overlay DOM
- `app/static/studio.css` — 前台退出确认弹层样式（可复用/扩展 `sk-self-service-overlay`）
- `app/static/admin-studio.css` — 后台退出确认弹层样式
- `app/static/frontend.js` — `confirmLogout()` 改为操作专用 overlay，移除对 `openModal` 的依赖
- `app/static/admin.js` — 对称实现
- `openspec/specs/web-static-client-shells/spec.md` — 合并本变更 delta
- `ui-design.md`（可选）— 更新「退出确认」行，标明已统一为 Studio/Admin 模态
