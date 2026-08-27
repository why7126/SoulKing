## Context

当前登录页（`login.html`）与前台修改密码弹层（`index.html` 内 `#passwordOverlay`）的密码字段均为原生 `type="password"` 输入框，无显示/隐藏切换。登录页样式在 `login.css`，改密弹层使用 `studio.css` 中的 `sk-form-field` 体系。两者均为纯静态 HTML + 原生 JS，无前端框架。

## Goals / Non-Goals

**Goals:**

- 登录页 1 个密码字段、改密弹层 3 个密码字段均支持点击切换显示/隐藏。
- 交互与视觉与现有深色 Studio 主题一致；切换按钮位于输入框右侧内部（常见 password field 模式）。
- 提供轻量可复用实现：共享 CSS 组件 class 与 JS 初始化函数，避免三处重复逻辑。
- 满足基本可访问性：`button type="button"`、`aria-label`（显示密码 / 隐藏密码）、`aria-pressed` 反映当前状态。

**Non-Goals:**

- 后台管理端用户创建/重置密码模态（`admin.js` 内 `openModal` prompt）——不在本次范围。
- 密码强度指示器、复制到剪贴板等扩展功能。
- 后端或 API 变更。

## Decisions

### 1. DOM 结构：password-input 包装器

在每个密码 `<input>` 外包一层容器，例如：

```html
<div class="password-input">
  <input type="password" … />
  <button type="button" class="password-toggle" aria-label="显示密码" aria-pressed="false">…</button>
</div>
```

- **理由**：右侧内嵌按钮需 `position: relative` 容器与 input 右侧 padding，避免文字与按钮重叠。
- **备选**：仅用 CSS `::-ms-reveal` 等浏览器原生控件——不可控且 WebKit 支持不一致，弃用。

### 2. 切换图标：内联 SVG 或 Unicode

使用内联 SVG（眼睛开/闭）或简洁 Unicode（👁），通过 `aria-hidden="true"` 装饰，语义由 `aria-label` 承担。

- **理由**：不引入新静态资源或 icon 库；与项目现有 inline SVG 风格（若有）或纯 CSS 按钮一致。
- **登录页**使用 `login.css` 中 `.password-input` 变体；**前台弹层**在 `studio.css` 的 `.front-app .sk-form-field .password-input` 下定义，复用相同 BEM 命名。

### 3. JS：共享 `initPasswordToggle(container)` 函数

在 `frontend.js` 中定义通用函数，对容器内 `.password-input` 绑定 click handler：切换 `input.type` 在 `password` ↔ `text`，同步更新按钮 `aria-label`、`aria-pressed` 与图标状态。

- **登录页**（`login.js`）：页面加载后对 `#loginPassword` 的包装器调用，或复制同等 5–10 行逻辑（登录页不加载 `frontend.js`）。
- **改密弹层**：在现有 DOMContentLoaded / 初始化段对 `#passwordOverlay` 调用一次，自动处理三个字段。
- **/ **理由**：登录页独立脚本，不宜强依赖前台模块；逻辑足够小，允许 `login.js` 内联等价实现或抽取到可选共享 `password-toggle.js`（若未来第三 files 则再抽）。**首选**：`login.js` 与 `frontend.js` 各含相同小函数，避免新增共享文件与 login 页额外请求——符合最小 diff 原则。

### 4. 打开改密弹层时重置为隐藏态

`openPasswordOverlay()` 清空输入值时，须将各字段 `type` 重置为 `password`，并将切换按钮 `aria-pressed` 设为 `false`。

- **理由**：避免用户上次切换为明文后，下次打开弹层仍暴露密码。

### 5. 样式细节

- Input 右侧增加 padding（如 `padding-right: 2.5rem`）。
- Toggle 按钮：透明背景、muted 色图标、hover 略亮；focus 可见 outline。
- 不改变现有 `autocomplete` 属性（`current-password` / `new-password`）。

## Risks / Trade-offs

- **[Risk] 明文显示时 shoulder surfing** → 默认仍为隐藏；用户主动切换才显示，符合行业惯例。
- **[Risk] `type=text` 时浏览器可能禁用 autocomplete 行为差异** → 仅临时切换，提交前可保持用户选择；不影响服务端。
- **[Risk] login.js 与 frontend.js 重复小函数** → 可接受；两处逻辑 <15 行，后续可抽共享脚本若 DRY 需求上升。
