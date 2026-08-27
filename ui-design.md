# SoulKing UI / UE 设计规范

本文档描述 ProjectMusic Web 客户端的**实际**视觉与交互约定，与 `app/static/` 中样式文件一一对应。项目采用 **「全局基础层 + 壳皮肤层」** 双层 CSS 架构，而非单一主题。

---

## 1. 样式分层总览

| 层级 | 文件 | 作用域 | 说明 |
|------|------|--------|------|
| 全局基础 | `styles.css` | 全站 `:root` | Hermes Pure Ink 灰阶令牌、布局壳（`app-shell`）、滚动条、Toast、通用模态（`.modal-overlay` / `.modal-card`）、历史表单与表格组件 |
| 前台皮肤 | `studio.css` | `.front-app` | SoulKing Studio：深 charcoal + 紫色强调，`--sk-*` 令牌 |
| 后台皮肤 | `admin-studio.css` | `.admin-app` | SoulKing Admin：与前台同系深色 + 紫色，`--adm-*` 令牌 |
| 登录页 | `login.css` | `.login-page` | 独立居中卡片；色值接近 Studio，但未引用 `--sk-*` |

### 各页面引用关系

| 页面 | HTML | 样式栈 |
|------|------|--------|
| 前台壳 | `index.html` | `styles.css` → `studio.css` |
| 后台壳 | `admin.html` | `styles.css` → `admin-studio.css` |
| 登录页 | `login.html` | `studio.css` → `login.css` |

**原则：** 壳内新增 UI **优先使用对应皮肤层的 `--sk-*` / `--adm-*` 与 `btn-studio-*` / `btn-adm-*`**；仅当复用全局模态、Toast、布局壳等基础设施时才依赖 `styles.css` 的 Hermes 令牌。

---

## 2. SoulKing Studio（前台 · `studio.css`）

前台首页（`index.html`，`body.front-app`）实现独立视觉体系：**深 charcoal 背景 + 紫色强调色**。

### 2.1 布局

```
┌─────────────┬──────────────────────────────────────────┬──────────────┐
│  侧栏导航    │  顶栏（搜索 / 操作）                       │              │
│  sk-nav     ├──────────────────────────────────────────┤  Inspector   │
│  248px      │  中部主内容（曲库表 / 歌单 / 详情）          │  320px       │
│             ├──────────────────────────────────────────┤              │
│  底部用户区  │  底部播放条（transport + 歌词行）           │              │
└─────────────┴──────────────────────────────────────────┴──────────────┘
```

- 侧栏展开宽度：`--sk-sidebar-w: 248px`；收起：`--sidebar-w-collapsed: 64px`（定义于 `styles.css`）
- 右侧 Inspector：`--sk-inspector-w: 320px`
- 顶栏高度：`--sk-header-h: 56px`
- 播放条总高：`--sk-player-total-h`（含控件行 + 歌词行；隐藏歌词时用 compact 变量）

交互逻辑见 `frontend.js`：表格行选、Inspector 元数据环、播放器、⌘K 聚焦搜索等。

### 2.2 色彩与设计令牌（`.front-app`）

| 变量 | 用途 | 值 |
|------|------|-----|
| `--sk-bg` | 页面底色 | `#0B0C14` |
| `--sk-panel` | 卡片、表格容器、输入背景 | `#151621` |
| `--sk-panel-2` | 次级面板（用户菜单等） | `#1A1B26` |
| `--sk-border` | 边框 / 分隔 | `rgba(148,163,184,0.12)` |
| `--sk-accent` | 主按钮、选中态、环形进度 | `#8B5CF6`（侧栏内局部覆写为 `#6C47FF`） |
| `--sk-accent-hover` | 悬停 / 高亮文字 | `#A78BFA` |
| `--sk-accent-muted` | 选中背景、淡紫底 | `rgba(139,92,246,0.18)` |
| `--sk-text` | 主文案 | `#FFFFFF` |
| `--sk-muted` | 次级文案 | `#94A3B8` |
| `--sk-muted-2` | 更弱文案（搜索图标等） | `#64748B` |
| `--sk-success` | 成功态 | `#10B981` |
| `--sk-danger` | 危险 / 退出登录 | `#F87171` |
| `--sk-radius` | 卡片圆角 | `10px` |
| `--sk-radius-sm` | 按钮、输入圆角 | `8px` |

侧栏背景：`linear-gradient(180deg, #12131C 0%, #0B0C14 45%)`。页面装饰性 `.bg-orb` 在 Studio 下透明度降至 `0.12`。

### 2.3 组件模式

**按钮（均在 `.front-app` 下）：**

| Class | 用途 |
|-------|------|
| `btn-studio-primary` | 主操作（紫渐变 + 阴影） |
| `btn-studio-secondary` | 次要操作（面板底 + 边框） |
| `btn-studio-ghost` | 工具栏 / 播放条弱操作 |
| `btn-studio-ai-outline` | AI 相关描边按钮 |

**导航：**

- 主导航：`sk-nav` + `sk-nav-item`；选中态 `is-active`（紫色 muted 底 + 左边条）
- 媒体类型切换：`sk-tier-nav` + `sk-tier-btn`（音乐 / 图片 / 视频占位）

**搜索 / 输入：**

- 顶栏与列表内搜索：`.studio-search-wrap input`
- 背景 `var(--sk-panel)`，边框 `var(--sk-border)`
- Focus：`border-color: rgba(139,92,246,0.45)` + `box-shadow: 0 0 0 3px rgba(139,92,246,0.12)`

**侧栏用户菜单：**

- 容器：`sk-user-menu`（向上弹出，`--sk-panel-2` 背景）
- 菜单项：`sk-user-menu-item`；hover 为 `rgba(255,255,255,0.06)`
- 危险项：`user-menu-item--destructive`（顶部分隔线 + `--sk-danger` 字色 + 淡红 hover 底）
- 菜单项：个人资料、修改密码、进入后台（仅 admin）、退出登录

**Toast / 通用模态 / 自助表单：**

- Toast 与歌单等通用 `#modalOverlay` 确认仍走 **`styles.css` 全局 Hermes 模态**（灰阶 `--panel`）
- 「个人资料 / 修改密码 / 退出登录确认」使用 **`sk-self-service-overlay` + `sk-modal-card`**（Studio 皮肤，见 `studio.css`）；退出确认主按钮为 `btn-studio-danger`
- **个人资料**：可改昵称与头像；**用户名只读**（`#profileUsernameDisplay` + `sk-form-field--readonly`），前台不提交 `username`
- **头像展示**：侧栏 `#frontUserMenuBtn` 与 `#profileAvatarPreview` 须**原样**使用 `/auth/me` 或上传响应中的 presigned `avatar_url`（不得在客户端追加未签名查询参数，否则会 403）。同键覆盖时依赖每次重新签发的 URL 及上传时对象的 `Cache-Control`；选文件预览可用 `blob:` URL
- **修改密码**：当前密码、新密码、**确认新密码**；`#passwordSaveBtn` 默认 `disabled`，仅当当前密码已填、两次新密码一致且满足复杂度时可点

---

## 3. SoulKing Admin（后台 · `admin-studio.css`）

管理页（`admin.html`，`body.admin-app`）与前台共用深色 + 紫色语言，令牌前缀为 `--adm-*`。

### 3.1 布局

```
┌─────────────┬──────────────────────────────────────────┬──────────────┐
│  侧栏全量菜单 │  页头统计卡                                │              │
│  adm-nav    ├──────────────────────────────────────────┤  内嵌编辑     │
│  248px      │  工具栏 + 快捷筛选 + 数据表                  │  抽屉 480px   │
│             ├──────────────────────────────────────────┤              │
│  底部用户区  │  表底批量操作 + 分页                        │              │
│             ├──────────────────────────────────────────┤              │
│             │  底部试听条                                 │              │
└─────────────┴──────────────────────────────────────────┴──────────────┘
```

- 编辑抽屉宽度：`--adm-edit-w: 480px`；打开时主内容区 `margin-right` 让位
- 交互见 `admin.js`：行选编辑、⌘K 搜索、客户端分页、AI 建议面板等

### 3.2 色彩与设计令牌（`.admin-app`）

| 变量 | 用途 | 值 |
|------|------|-----|
| `--adm-bg` | 页面底色 | `#0D0D14` |
| `--adm-panel` | 卡片、表格 | `#161621` |
| `--adm-panel-2` | 次级面板 | `#1C1C28` |
| `--adm-border` | 边框 | `rgba(148,163,184,0.14)` |
| `--adm-accent` | 主强调 | `#6C47FF` |
| `--adm-accent-hover` | 悬停 | `#A78BFA` |
| `--adm-accent-muted` | 选中底 | `rgba(124,77,255,0.18)` |
| `--adm-text` / `--adm-muted` / `--adm-muted-2` | 文案层级 | 同前台语义 |
| `--adm-success` / `--adm-warn` / `--adm-danger` | 状态色 | `#10B981` / `#F59E0B` / `#F87171` |
| `--adm-radius` / `--adm-radius-sm` | 圆角 | `10px` / `8px` |

### 3.3 组件模式

**按钮：** `btn-adm-primary` / `btn-adm-secondary` / `btn-adm-ghost` / `btn-adm-sm`（均在 `.admin-app` 下）

**用户菜单：** `adm-user-menu` + `adm-user-menu-item`；结构与前台对称，仅含「返回前台」「退出登录」。个人资料 / 改密在前台用户菜单完成。退出登录确认使用 **`adm-self-service-overlay` + `adm-modal-card`**（非 Hermes `#modalOverlay`），主按钮 `btn-adm-danger`。

**模态：** 新建 / 编辑 / 删除 / 合并等弹层使用 **`styles.css` 全局 `.modal-overlay` / `.modal-card`**（Hermes 灰阶），表单控件混用 `btn-adm-*` 与全局 `btn` / `btn-primary`。

**参考数据管理页（艺人 / 标签 / 语言 / 用户）：** 与歌曲管理共用 `admin-studio-root` → `adm-page-header` → `adm-controls`（`adm-toolbar` + `adm-search-wrap`）→ `adm-workspace` → `adm-table-scroll` + `adm-data-table` + `adm-table-footer`（`adm-list-total` + `adm-pagination`）。表头排序控件类名可为 `manager-sort-btn`，视觉与 `sort-btn` 一致；批量删除使用 `btn-adm-ghost btn-adm-danger`。操作列 `.col-actions` 仅展示 ⋮「更多」，行级操作在 `.table-more-menu` 内（与歌曲列表相同）。

| 页面 | 搜索 placeholder | 底栏计数单位 |
|------|------------------|--------------|
| 艺人管理 | 搜索艺人… | 位艺人 |
| 标签管理 | 搜索标签… | 个标签 |
| 语言管理 | 搜索语言… | 种语言 |
| 用户管理 | 搜索用户名 / 昵称… | 位用户 |

---

## 4. 登录页（`login.css`）

独立全屏居中卡片，**不**挂载 `body.front-app`，因此不自动继承 `--sk-*`。

| 元素 | 约定 |
|------|------|
| 背景 | `#0F0F14` |
| 卡片 | `#18181F`，圆角 16px，细白描边 + 深阴影 |
| 字段 | `login-field`：标签 `#9CA3AF`，输入 `#0F0F14` 底 |
| Focus | 紫色描边 `rgba(139,92,246,0.5)` / `#8B5CF6` |
| 提交 | `login-submit`：紫渐变 `#7C3AED` → `#8B5CF6` |

色相向 Studio 靠拢，但变量未与 `--sk-*` 打通；后续可统一引用 Studio 令牌。

---

## 5. Hermes 全局层（`styles.css` · 历史参照）

沉淀自 **[hermes-web-ui](https://github.com/EKKOLearnAI/hermes-web-ui)**（Vue 3 + Naive UI）的 Pure Ink 灰阶体系，作为**跨壳基础设施**，不再作为前台 / 后台主视觉。

### 5.1 设计命题：Pure Ink（黑白水墨）

- 主路径以黑、白、灰构成层次；状态色保留功能性色相
- 默认暗色盘面，与上游 `variables.scss` `.dark` 块对齐

### 5.2 `:root` 色彩令牌

| 语义 | 变量 | 十六进制 |
|------|------|----------|
| 页面背景 | `--bg` | `#1A1A1A` |
| 次级背景 | `--bg-soft` | `#252525` |
| 卡片 / 面板 | `--panel` | `#2A2A2A` |
| 分割线 / 边框 | `--stroke` | `#3A3A3A` |
| 主文案 | `--text` | `#F0F0F0` |
| 弱化文案 | `--muted` | `#888888` |
| 主操作色（非彩） | `--accent` | `#E0E0E0` |
| 主按钮字色 | `--accent-on-accent` | `#1A1A1A` |
| RGB 分量 | `--accent-rgb` | `224, 224, 224` |
| 危险 | `--danger` | `#EF5350` |
| 弹层遮罩 | `--admin-modal-scrim` | `rgba(0,0,0,0.68)` |

### 5.3 全局组件

| 组件 | Class / 约定 |
|------|----------------|
| 布局壳 | `app-shell`、`app-sidebar`、侧栏收起 `is-sidebar-collapsed` |
| 通用按钮 | `btn`、`btn-primary`（灰白主色，非 Studio 紫） |
| Toast | `.toast-container` / `.toast` / `.toast.error` / `.toast.success` |
| 通用模态 | `.modal-overlay`、`.modal-card`（默认宽 `min(720px,96vw)`，圆角 10px） |
| 滚动条 | 宽 6px，thumb 使用 `--stroke` |
| Focus（全局） | `outline: 2px solid rgba(var(--accent-rgb),0.55)` |

### 5.4 上游源码对照

| 类别 | 路径 |
|------|------|
| Naive UI 主题覆盖 | `packages/client/src/styles/theme.ts` |
| CSS 变量 | `packages/client/src/styles/variables.scss` |
| 全局排版 | `packages/client/src/styles/global.scss` |

---

## 6. 跨壳 UE 约定

### 6.1 字体

| 用途 | 来源 |
|------|------|
| 界面 | Google Fonts `Inter` + `system-ui` 回退 |
| 等宽 | Google Fonts `JetBrains Mono` |

字号基准 **14px**（`body` / 壳内控件多为 **13px** 按钮与表头）。

### 6.2 形状与间距

- 卡片 / 面板圆角：**10px**（`--sk-radius` / `--adm-radius`）
- 按钮 / 输入圆角：**8px**
- Hover：低透明度白叠加 `rgba(255,255,255,0.06)` 量级，避免高饱和光晕
- 侧栏收起动画：`width 0.2s ease`

### 6.3 交互模式

- **⌘K / Ctrl+K**：前台、后台均聚焦主搜索框
- **用户菜单**：点击侧栏头像按钮展开；点击外部或选择菜单项后关闭；退出登录先关菜单再 Studio/Admin 专用确认弹层（`#logoutConfirmOverlay`）
- **前后台跳转**：整页导航（`/admin` ↔ `/`）
- **版本徽标**：`app-brand-version` 展示应用版本（前台 / 后台品牌行）

### 6.4 占位与示意 UI

- 侧栏「AI 管理 / 系统」等待开发项：`is-placeholder`，提示「即将推出」
- 前台存储进度条为示意 UI
- 顶栏「导入音乐 / 扫描目录」跳转后台音乐管理

---

## 7. 维护约定

1. **前台壳内新 UI** → 使用 `studio.css` 与 `--sk-*`；禁止在前台页引用仅定义于 `login.css` 的 class（如 `login-field`）。
2. **后台壳内新 UI** → 使用 `admin-studio.css` 与 `--adm-*`。
3. **跨壳共享能力**（Toast、确认模态、布局壳）→ 可继续用 `styles.css`，但应知晓其为 Hermes 灰阶，与 Studio 主界面视觉不同。
4. **半透明描边 / 发光** → Studio / Admin 侧优先 `rgba(139,92,246,α)` 或对应 `--sk-accent-muted`；Hermes 侧用 `rgba(var(--accent-rgb),α)`。
5. **新增模态决策树：**
   - 前台主界面内的表单 / 面板 / 退出登录确认 → Studio 皮肤（`sk-*` 前缀）
   - 歌单等简短确认 / 其它 destructive 二次确认 → 可暂用全局 `#modalOverlay`
   - 后台退出登录确认 → `adm-self-service-overlay`；其它 CRUD 弹窗 → 当前沿用全局 `.modal-card` + Admin 按钮混排
6. 修改令牌或组件模式后 **同步更新本文档** 对应章节。

---

## 8. 已知视觉不一致（待对齐）

| 区域 | 现状 | 目标 |
|------|------|------|
| 前台 `#modalOverlay` 确认框（歌单等） | Hermes 灰阶 | 可选后续统一为 Studio 模态 |
| 登录页 | `login.css` 硬编码色值 | 可选引用 `--sk-*` |
| 后台 CRUD 模态 | Hermes `.modal-card` | 可选后续 Admin 专用模态 |

---

## 9. 参考链接

- Hermes 上游：<https://github.com/EKKOLearnAI/hermes-web-ui>
- 前台脚本：`app/static/frontend.js`
- 后台脚本：`app/static/admin.js`
- OpenSpec 视觉对齐变更：`openspec/changes/align-profile-password-ui-with-studio-design/`
