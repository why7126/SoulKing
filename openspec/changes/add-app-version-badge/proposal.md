## Why

当前前台与后台壳在 UI 中无法识别正在运行的产品版本，开发者与内测用户只能通过代码或文档（如 `iterations/release_list.md`）推断部署版本，不利于确认环境、排查问题与发版对齐。需要在壳层展示统一、低干扰的版本标识，并与发版流程挂钩。

## What Changes

- **版本数据源**：新增 `app/static/version.js` 导出 `APP_VERSION`（初始值 `v0.0.6`）；在 `app/config.py` 的 `Settings` 中新增 `app_version` 字段（初始值 `0.0.6`，与前端语义一致）。发版时两处由开发者手工同步更新。
- **前台品牌区角标**：在侧栏品牌标题「SoulKing」旁展示方案 A 角标（小字 muted、`JetBrains Mono`），读取 `version.js` 渲染；收起侧栏时随 `.sk-brand-text` 一并隐藏。
- **后台品牌区角标**：与前台同一版本值、同一套共享样式类，挂载于 `.adm-brand-title` 旁；收起侧栏时默认隐藏。
- **共享样式**：在 `app/static/styles.css` 定义壳无关的 `.app-brand-version` 样式，前台 `studio.css` 与后台 `admin-studio.css` 不重复定义。
- **文档页 `<title>`**（可选补充）：前台/后台 `<title>` 可附带版本前缀或后缀，便于多标签页区分。
- 递增相关 HTML/CSS/JS 的 `?v=` 静态资源缓存版本。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：新增前台与后台壳侧栏品牌区产品版本角标的展示、数据源、收起态隐藏及与静态资源 `?v=` 缓存版本参数的区分说明。

## Impact

- **后端配置**：`app/config.py`（`app_version` 字段，供日志/健康检查等后续可选读取）。
- **前端静态**：新增 `app/static/version.js`；修改 `app/static/index.html`、`app/static/admin.html`（引用 `version.js`、品牌区 DOM）；`app/static/styles.css`（共享角标样式）；可选微调 `studio.css` / `admin-studio.css`（若需壳内布局对齐）。
- **发版流程**：与 `iterations/release_list.md` 并列维护——`release_list.md` 记录变更说明，`config.py` + `version.js` 记录当前运行版本号。
- **API**：无新增端点；本变更不要求首屏 fetch 版本接口。
