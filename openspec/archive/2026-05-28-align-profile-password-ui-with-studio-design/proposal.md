## Why

用户认证能力上线后，前台壳「个人资料」「修改密码」弹层复用了全局 `styles.css` 的 Hermes 灰阶模态样式与 `login-field` 类名，但 `login.css` 未在前台页加载，且整体视觉令牌与 `ui-design.md` 定义的 SoulKing Studio 深色 + 紫色强调体系不一致，导致自助表单在背景色、边框、按钮与输入框焦点态上与侧栏、顶栏、表格等区域明显割裂，影响产品一致性与可用性感知。

## What Changes

- 为前台壳个人资料与修改密码弹层引入 **Studio 皮肤** 专用样式（`studio.css`），使用 `--sk-*` 设计令牌，与 `ui-design.md` 中 SoulKing Studio 规范对齐。
- 将弹层 HTML 中的 `login-field`、`btn` / `btn-primary` 等跨页/后台类名替换为 Studio 语义化结构（如 `sk-modal-*`、`sk-form-field`、`btn-studio-primary` / `btn-studio-secondary`）。
- 统一弹层尺寸、圆角、遮罩、标题栏、操作区布局与壳内其它 Studio 控件（搜索框、按钮）的交互反馈（紫色 focus ring、hover 叠加）。
- 个人资料弹层补充当前头像预览（若有 `avatar_url`），与侧栏头像展示一致。
- 修改密码弹层保留复杂度提示文案，样式与 Studio 弱化文案层级一致。
- 更新 `web-static-client-shells` 与 `user-self-service` 能力 spec，明确前台自助表单的视觉与结构验收要求。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：补充前台壳个人资料/修改密码弹层须使用 Studio 设计令牌与组件样式的验收场景。
- `user-self-service`：补充前台自助表单 UI 与 Studio 皮肤一致、头像预览等非 API 行为约束。

## Impact

- `app/static/index.html` — 个人资料与修改密码弹层 DOM 结构与 class
- `app/static/studio.css` — Studio 模态与表单字段样式（新增）
- `app/static/frontend.js` — 头像预览渲染（若需动态更新 DOM）
- `ui-design.md` — 可选补充「前台自助模态」维护约定（若实现中沉淀新模式）
- `openspec/specs/web-static-client-shells/spec.md` — 主 spec 合并 delta
- `openspec/specs/user-self-service/spec.md` — 主 spec 合并 delta
