## ADDED Requirements

### Requirement: 前台壳个人资料与修改密码弹层 Studio 视觉

前台壳内 `#profileOverlay` 与 `#passwordOverlay`（或等价自助表单模态）SHALL 使用 SoulKing Studio 设计令牌与组件样式，与 `ui-design.md` 及 `studio.css` 中 `--sk-*` 体系一致；MUST NOT 依赖未在前台页加载的 `login.css` 或 Hermes 灰阶 `--panel` / `--accent` 作为主视觉。

弹层 SHALL 满足：

- 遮罩与卡片背景使用 `--sk-bg` / `--sk-panel` 层级；
- 主操作按钮使用 `btn-studio-primary`，次要操作使用 `btn-studio-secondary`（或等价 Studio 按钮 class）；
- 文本输入框边框、背景与 focus 态与壳内 Studio 搜索框/input 模式一致（紫色 focus ring）；
- 弹层 DOM 结构 MUST 使用 Studio 作用域 class（如 `sk-self-service-overlay`、`sk-modal-card`、`sk-form-field`），不得使用仅定义于 `login.css` 的 `login-field`。

#### Scenario: 个人资料弹层使用 Studio 令牌

- **GIVEN** 用户已登录并打开前台壳
- **WHEN** 用户从侧栏用户菜单激活「个人资料」
- **THEN** 弹层卡片背景与边框视觉与 Studio 面板（如曲库区域）一致
- **AND** 「保存」按钮呈现 Studio 紫色主按钮样式
- **AND** 输入框获得焦点时呈现紫色 focus ring

#### Scenario: 修改密码弹层使用 Studio 令牌

- **GIVEN** 用户已登录并打开前台壳
- **WHEN** 用户从侧栏用户菜单激活「修改密码」
- **THEN** 弹层视觉与个人资料弹层同属 Studio 皮肤
- **AND** 复杂度提示文案使用 Studio 弱化文字色（`--sk-muted` 量级）

#### Scenario: 不依赖 login.css

- **GIVEN** 前台壳 HTML 未引用 `login.css`
- **WHEN** 用户打开个人资料或修改密码弹层
- **THEN** 表单字段与按钮仍具备完整 Studio 样式
- **AND** 页面中不存在仅因缺少 `login.css` 导致的未样式化输入框
