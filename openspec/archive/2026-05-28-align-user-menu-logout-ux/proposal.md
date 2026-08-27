## Why

前台与后台壳侧栏用户菜单中的「退出登录」在视觉层次、分组与交互上不一致：后台已用危险色强调最后一项，前台仍为普通菜单项样式；前台四项菜单缺少「账户操作」与「结束会话」的分组；两边点击退出均直接 toast，无确认步骤，与产品内其它危险操作（如删除确认）体验不对齐。需要在不改变菜单定位与收起态行为的前提下，统一前后台退出登录的 UI/UE，并补齐 spec 约束，避免再次漂移。

## What Changes

- 为前后台用户菜单的「退出登录」项引入显式危险样式 class（`user-menu-item--destructive`），使用各壳 `--sk-danger` / `--adm-danger` 色值与一致的 hover 背景；移除后台仅依赖 `:last-child` 的隐式着色。
- 在用户菜单中为「退出登录」增加顶部分隔（细线或等价间距），前台在「进入后台」与「退出登录」之间分组；后台在「返回前台」与「退出登录」之间同样加分隔，使两项菜单结构对称。
- 用户激活「退出登录」时，前后台均先关闭用户菜单，再通过既有 `#modalOverlay` 展示确认对话框（取消 / 确认退出）；确认后执行与现网一致的演示反馈（toast）；取消则仅关闭对话框，不执行退出。
- 更新 `web-static-client-shells` 能力 spec，明确危险项样式、分组与确认流程的验收场景。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充前台与后台壳侧栏用户菜单中「退出登录」的危险操作视觉、菜单项分组分隔，以及退出前确认对话框的行为与验收要求。

## Impact

- `app/static/index.html` — 前台用户菜单 HTML（退出项 class、可选分隔元素）
- `app/static/admin.html` — 后台用户菜单 HTML（同上）
- `app/static/studio.css` — 前台用户菜单危险项与分隔样式；移除对 `:last-child` 的依赖需求
- `app/static/admin-studio.css` — 后台用户菜单危险项与分隔样式；删除或替换 `:last-child` 规则
- `app/static/frontend.js` — 退出登录确认流程（`openModal`）
- `app/static/admin.js` — 退出登录确认流程（`openModal`）
- `openspec/specs/web-static-client-shells/spec.md` — 主 spec 合并本变更 delta
