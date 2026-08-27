## Context

前台（`index.html` + `studio.css`）与后台（`admin.html` + `admin-studio.css`）均在侧栏顶部展示品牌区：Logo + 标题「SoulKing」+ 副标题。侧栏已支持收起/展开，收起时 `.sk-brand-text` / `.adm-brand-text` 整体 `display: none`。

产品版本目前仅记录在 `iterations/release_list.md`，UI 与 `config.py` 均无版本字段。静态 HTML 由 `FileResponse` 直出，无服务端模板注入。HTML 中的 `?v=` 查询参数仅用于缓存刷新，OpenSpec 已明确不作为产品版本。

## Goals / Non-Goals

**Goals:**

- 在前台与后台侧栏品牌标题旁展示统一的产品版本角标（方案 A：标题右侧小 badge）。
- 版本由开发者发版时手工维护，前台读取 `version.js`，后端 `config.py` 同步存储供非 UI 场景使用。
- 收起侧栏时版本角标默认隐藏（随品牌文案区隐藏）。
- 前后台复用同一套共享 CSS 类，视觉一致。

**Non-Goals:**

- 不新增 `/api/version` 或首屏异步拉取版本。
- 不将静态资源 `?v=` 与产品版本号绑定或自动推导。
- 不在用户菜单「关于」页展示更新日志（可后续独立变更）。
- 不要求 CI 自动 bump 版本（保持手工发版流程）。

## Decisions

### 1. 双源维护：`config.py` + `version.js`

**选择**：`Settings.app_version: str = "0.0.6"`（无 `v` 前缀，便于比较/日志）；`version.js` 导出 `export const APP_VERSION = "v0.0.6"`（带 `v` 前缀，直接用于 UI）。

**理由**：静态 HTML 无法从 Python 注入；前端必须有一份 JS 常量。后端保留字段便于健康检查、日志或未来 API 扩展，与现有 `app_name` 配置模式一致。

**备选**：仅 `version.js` —— 后端无法感知版本，放弃。**不采用**。

**发版约定**：每次发版同时更新 `config.py`、`version.js` 与 `release_list.md` 新段落。

### 2. 渲染方式：模块脚本初始化 DOM

**选择**：`index.html` / `admin.html` 在品牌标题内预留 `<span class="app-brand-version" id="appBrandVersion" aria-hidden="true"></span>`（或通过小 inline module 从 `version.js` import 后写入 `textContent` 与 `aria-label`）。

**理由**：避免在 HTML 硬编码版本导致前后台 drift；与现有 ES module 入口（`frontend.js` / `admin.js`）风格一致。可选在壳入口脚本最早阶段执行 `applyAppVersion()`，或单独 `version-init.js` 极短模块。

**备选**：构建时替换占位符 —— 当前无构建流水线，**不采用**。

### 3. 样式位置：共享 `styles.css`

**选择**：在 `styles.css` 定义 `.app-brand-title-row`（flex 对齐标题与角标）与 `.app-brand-version`（9–10px、`JetBrains Mono`、`var(--muted)` 或壳内 muted 令牌、可选极淡边框/圆角）。

**理由**：前后台已共用 `styles.css` 布局令牌；避免在 `studio.css` 与 `admin-studio.css` 各写一份。

**布局示意**：

```
┌─────────────────────────────────────┐
│ [Logo]  SoulKing  v0.0.6      [◀]  │
│         AI 音乐资料库                 │
└─────────────────────────────────────┘
         ↑ .app-brand-version
```

### 4. 收起态：随 `.sk-brand-text` / `.adm-brand-text` 隐藏

**选择**：版本 span 放在品牌文案容器内（标题行），不单独处理；现有收起 CSS 已隐藏整个 `.sk-brand-text`。

**理由**：符合用户「收起侧栏时默认隐藏」；零额外逻辑。

### 5. `<title>` 补充（可选）

**选择**：壳初始化时将 `document.title` 前缀或后缀追加 `APP_VERSION`（如 `SoulKing v0.0.6 · AI 音乐资源库`），与角标同源。

**理由**：多标签页/debug 友好，成本低。**若实现时觉得冗余可省略**，不影响角标验收。

## Risks / Trade-offs

- **[Risk] `config.py` 与 `version.js` 不同步** → 在 `tasks.md` 与 README/发版清单中明确「三处同改」；可选后续加简单 lint 脚本比对。
- **[Risk] 普通用户看到版本号** → 角标 muted 小字，低干扰；属内测/运维友好设计。
- **[Trade-off] 双源维护成本** → 换取后端可读性与静态前端零请求；对个人 MVP 可接受。

## Migration Plan

1. 新增 `version.js` 与 `config.py` 字段。
2. 更新 HTML 品牌区结构与脚本引用；添加共享 CSS。
3. Bump 相关 `?v=` 缓存参数。
4. 部署后目视确认前台/后台展开态显示相同版本，收起态隐藏。

**回滚**：删除角标 DOM/CSS 与 `version.js` 引用；`config.py` 字段可保留（无害）。

## Open Questions

（无 —— 方案 A、双源维护、收起隐藏均已由产品确认。）
