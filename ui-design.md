# SoulKing UI / UE 设计规范

## SoulKing Studio（前台 · 设计稿一比一复刻）

前台首页（`app/static/index.html`）使用 **`studio.css`** 实现独立视觉体系：**深 charcoal 背景 + 紫色强调色**，布局为 **左侧主导航 / 顶栏搜索与操作 / 中部表格曲库 / 右侧详情 Inspector / 底部播放条**。交互逻辑见 `frontend.js`（表格行、右侧元数据完整度环、播放器进度与快捷键 ⌘K 等）。

## SoulKing Admin（管理后台 · 设计稿一比一复刻）

管理页（`app/static/admin.html`）使用 **`admin-studio.css`**，与前台共用深色 + 紫色令牌。布局为 **侧栏全量菜单 / 页头统计卡 / 工具栏与快捷筛选 / 歌曲表 + 右侧内嵌编辑面板 / 表底批量与分页 / 底部试听条**。交互见 `admin.js`：行选打开编辑、⌘K 聚焦搜索、客户端分页与状态筛选、AI 建议面板等。

| CSS 变量 | 用途 | 参考值 |
|----------|------|--------|
| `--sk-bg` | 页面底色 | `#0B0C14` |
| `--sk-panel` | 卡片、表格容器 | `#151621` |
| `--sk-accent` | 主按钮、选中态、环形进度 | `#8B5CF6` |
| `--sk-muted` | 次级文案 | `#94A3B8` |

顶栏「导入音乐 / 扫描目录」跳转后台音乐管理；侧栏「AI 管理 / 系统」部分菜单为占位并提示「即将推出」。存储进度条为示意 UI。

---

## Hermes Web UI（后台与通用令牌 · 历史参照）

以下章节沉淀自开源项目 **[hermes-web-ui](https://github.com/EKKOLearnAI/hermes-web-ui)**（Vue 3 + Naive UI），提炼其视觉与交互意图；**后台管理页**仍以 `styles.css` 中 `:root` 灰阶令牌为主，与前台 Studio 皮肤分离。

**源码对照（上游）：**

| 类别 | 路径 |
|------|------|
| Naive UI 主题覆盖（明暗） | `packages/client/src/styles/theme.ts` |
| CSS 变量与 SCSS 令牌 | `packages/client/src/styles/variables.scss` |
| 全局排版、滚动条、页面头 | `packages/client/src/styles/global.scss` |
| 主题装配 | `packages/client/src/App.vue`（`NConfigProvider` + `darkTheme`） |

---

## 1. 设计命题：Pure Ink（黑白水墨）

- **色相策略**：界面主路径以**黑、白、灰**构成层次，避免彩色作为品牌主色；状态色（成功 / 警告 / 错误）保留功能性色相。
- **明暗**：上游同时支持浅色与深色主题；本项目的 Web 壳默认采用与上游 **`variables.scss` 中 `.dark`** 一致的暗色盘面，以保持控制台类产品的阅读舒适度。

---

## 2. 色彩令牌（暗色 — 应用映射）

与上游 `variables.scss` 的 `.dark` 块对齐，本项目在 `styles.css` 的 `:root` 中使用下列语义（名称保留历史变量以便少量改动现有选择器）：

| 语义 | 上游变量 | 本项目变量 | 十六进制 |
|------|-----------|------------|----------|
| 页面背景 | `--bg-primary` | `--bg` | `#1a1a1a` |
| 次级背景 | `--bg-secondary` | `--bg-soft` | `#252525` |
| 卡片 / 面板 | `--bg-card` | `--panel` | `#2a2a2a` |
| 分割线 / 边框 | `--border-color` | `--stroke` | `#3a3a3a` |
| 主文案 | `--text-primary` | `--text` | `#f0f0f0` |
| 次级文案 | `--text-secondary` | （与 muted 分层使用时） | `#c0c0c0` |
| 弱化文案 | `--text-muted` | `--muted` | `#888888` |
| 主操作色（非彩） | `--accent-primary` | `--accent` | `#e0e0e0` |
| 主按钮上的字色 | `--text-on-accent` | `--accent-on-accent` | `#1a1a1a` |
| RGB 分量（rgba） | `--accent-primary-rgb` | `--accent-rgb` | `224, 224, 224` |
| 危险 | `--error` | `--danger` | `#ef5350` |

Naive UI 侧对应关系见 `theme.ts` 中 `darkThemeOverrides.common`（如 `primaryColor`、`bodyColor`、`borderRadius` 等）。

---

## 3. 字体

| 用途 | 上游 | 本项目 |
|------|------|--------|
| 界面 | `Inter`, system-ui | Google Fonts：`Inter` |
| 等宽 | `JetBrains Mono`, `Fira Code`, … | Google Fonts：`JetBrains Mono`（代码块等需要时） |

字号基准：**14px**（与上游 `common.fontSize` 一致）；标题层级可在基准上递增，保持清晰对比而非过大装饰。

---

## 4. 形状与间距

- **圆角**：上游 Naive `borderRadius` 为 **8px**，小号 **6px**。本项目卡片/面板统一向 **10px** 靠拢（介于 upstream 的 md/sm 之间），避免过度圆角玩具感。
- **交互反馈**：悬停使用 **低透明度叠加**（上游 `hoverColor` 思路：`rgba(255,255,255,0.06)` 量级），而非高饱和色光晕。

---

## 5. 布局与组件模式（UE）

借鉴上游 Dashboard 结构（侧栏 + 主内容，`App.vue` + `AppSidebar`）：

- **顶栏**：左侧品牌区 + 中间导航（后台）+ 右侧主操作。
- **导航选中态**：浅色底条 + 对比足够的文字，而非渐变「科技感」高亮。
- **表单控件**：背景与输入框底色跟卡片层级区分（上游 `inputColor` vs `cardColor`）。
- **滚动条**：细轨道、thumb 与边框色同源（见 `global.scss` 滚动条段）。

---

## 6. 维护约定

- 新增样式时**优先使用** `:root` 中已有语义变量；若需半透明描边/发光，使用 `rgba(var(--accent-rgb), α)`，避免再次写死 RGB。
- 若未来需要浅色主题，可对照 `variables.scss` 的 `:root`（非 `.dark`）块增加 `html.light` 或类切换，并同步更新本文档「色彩令牌」表。

---

## 7. 参考链接

- 仓库：<https://github.com/EKKOLearnAI/hermes-web-ui>
- 技术栈说明：README 中 **Frontend: Vue 3 + TypeScript + Vite + Naive UI + …**
