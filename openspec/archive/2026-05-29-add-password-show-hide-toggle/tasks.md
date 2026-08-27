## 1. 共享样式与 DOM 结构

- [x] 1.1 在 `login.css` 增加 `.password-input` 包装器与 `.password-toggle` 按钮样式（右侧内嵌、input 右侧 padding、focus/hover 态）
- [x] 1.2 在 `studio.css` 为 `.front-app .sk-form-field .password-input` 增加等价样式，与 Studio 输入框 focus ring 一致

## 2. 登录页

- [x] 2.1 更新 `login.html`：为 `#loginPassword` 增加 `.password-input` 包装与切换按钮（含 `aria-label`、`aria-pressed`）
- [x] 2.2 在 `login.js` 实现切换逻辑：点击按钮在 `password`/`text` 间切换并更新 ARIA 状态

## 3. 前台修改密码弹层

- [x] 3.1 更新 `index.html` 中 `#passwordOverlay` 三个密码字段，各增加 `.password-input` 包装与切换按钮
- [x] 3.2 在 `frontend.js` 增加 `initPasswordToggles(container)`（或等价）并在页面初始化时对 `#passwordOverlay` 调用
- [x] 3.3 更新 `openPasswordOverlay()`：清空字段时将各 input 重置为 `type="password"`，切换按钮重置为隐藏态

## 4. 验收

- [x] 4.1 手动验证登录页：输入密码后切换显示/隐藏，提交登录仍正常
- [x] 4.2 手动验证改密弹层：三个字段独立切换；关闭再打开后均为掩码；保存改密流程不受影响
