## Context

`ui-design.md` 规定前台 SoulKing Studio 使用 `studio.css` 中的 `--sk-*` 令牌（深 charcoal 背景 `#0B0C14`、面板 `#151621`、紫色强调 `#8B5CF6`）。用户认证上线后，`index.html` 中 `#profileOverlay` 与 `#passwordOverlay` 仍使用全局 `styles.css` 的 Hermes 灰阶模态（`--panel` / `--stroke` / `--accent` 灰白系），表单字段复用 `login-field` 类名但 **未** 加载 `login.css`，导致输入框缺少正确样式；按钮使用 `btn` / `btn-primary` 而非 `btn-studio-*`。壳内搜索框、侧栏、播放条等已统一 Studio 视觉，自助弹层成为明显异类。

## Goals / Non-Goals

**Goals:**

- 个人资料与修改密码弹层在颜色、圆角、边框、按钮、输入 focus 态上与 Studio 壳一致。
- 复用或扩展现有 Studio 组件模式（`btn-studio-primary` / `btn-studio-secondary`、搜索框 input 样式），避免再引入 `login.css` 或 Hermes 令牌到前台页。
- 个人资料弹层展示当前头像预览（有 `avatar_url` 时显示图片，否则首字母占位），与侧栏头像逻辑一致。
- 保持现有 API 调用与 JS 行为（`openProfileOverlay` / `saveProfile` 等）不变，仅调整 DOM 结构与样式。

**Non-Goals:**

- 不改登录页（`login.html`）视觉；登录页可后续单独对齐 Studio。
- 不改后台壳模态（`admin.html` 仍用 Hermes / admin 混合样式）。
- 不改通用 `#modalOverlay` 确认框样式（歌单、退出登录等仍用现有全局模态，可后续统一）。
- 不新增路由或独立页面；仍为壳内 overlay。

## Decisions

### 1. 在 `studio.css` 新增前台作用域模态样式，而非覆盖全局 `.modal-overlay`

**选择：** 为 `#profileOverlay` / `#passwordOverlay` 使用专用 class 前缀 `sk-self-service-overlay` / `sk-modal-card`，样式写在 `.front-app` 下，引用 `--sk-*` 令牌。

**理由：** 全局 `.modal-card` 被后台与前台共用；若直接改 `styles.css` 会影响 admin 与其它前台确认框。作用域化可最小 diff、符合 `ui-design.md`「前台 Studio 独立视觉体系」。

**备选：** 统一所有前台 modals 到 Studio 皮肤 — 范围过大，留作后续变更。

### 2. 表单字段采用 `sk-form-field` 结构，对齐搜索框 input 令牌

**选择：** 标签 + input 的 flex 列布局；input 使用与 `.studio-search-wrap input` 相同的 background / border / focus ring（`var(--sk-panel)`、`var(--sk-border)`、紫色 `box-shadow`）。

**理由：** 已有成熟 pattern，无需新依赖；去掉对未加载的 `login-field` 的依赖。

### 3. 按钮使用既有 `btn-studio-primary` / `btn-studio-secondary`

**选择：** 取消与保存分别映射 secondary / primary；关闭按钮使用 ghost 或 icon 按钮样式，与壳内其它关闭控件一致。

**理由：** 与顶栏、工具栏按钮一致，零新 CSS 变量。

### 4. 头像预览：静态 HTML 容器 + JS 填充

**选择：** 在 `#profileOverlay` 增加 `#profileAvatarPreview`（圆形，尺寸与侧栏头像相近）；`openProfileOverlay()` 根据 `state.me.avatar_url` 设置 `img` 或首字母文本。

**理由：** 与 `user-self-service` 上传能力配套，用户改头像前可见当前状态；实现轻量。

### 5. 弹层宽度与布局

**选择：** 卡片宽度 `min(420px, 92vw)`（较通用 720px 模态更紧凑，适合 3–4 个字段）；标题栏 + 分隔线 + 表单 + 底栏操作区（右对齐按钮组）。

**理由：** 自助表单字段少，窄卡片更符合 Studio 面板密度；与 `ui-design.md` 10px 圆角一致。

## Risks / Trade-offs

- **[Risk] 前台存在多种模态视觉（Studio 自助 vs Hermes 通用确认框）** → 本变更仅覆盖自助两框；在 spec 中明确范围，避免误以为已全部统一。
- **[Risk] `file` input 原生样式在各浏览器不一致** → 使用 Studio 色系的自定义 file 区域或弱化原生控件边框，保证可读即可。
- **[Risk] 内联 `style="margin-bottom:12px"` 散落** → 重构时移入 CSS class，减少维护成本。

## Migration Plan

1. 在 `studio.css` 添加样式类。
2. 更新 `index.html` 弹层 markup。
3. 微调 `frontend.js` 头像预览逻辑。
4. 手动验收：打开个人资料/修改密码，对比侧栏/搜索框色值与 focus 态；保存流程回归。

无数据迁移；可逐文件部署，回滚即还原 HTML/CSS。

## Open Questions

（无 — 视觉对齐 `ui-design.md` Studio 章节，实现路径明确。）
