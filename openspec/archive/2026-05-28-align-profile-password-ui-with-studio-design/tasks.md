## 1. Studio 模态与表单样式

- [x] 1.1 在 `studio.css` 新增 `.front-app` 下 `sk-self-service-overlay`、`sk-modal-card`、`sk-modal-head`、`sk-modal-actions`、`sk-form-field` 等样式，使用 `--sk-*` 令牌（背景、边框、圆角、focus ring）
- [x] 1.2 为 `sk-form-field` 内 `input[type="text"]`、`input[type="password"]`、`input[type="file"]` 定义与 Studio 搜索框一致的交互态
- [x] 1.3 新增 `#profileAvatarPreview` 圆形头像预览样式（尺寸与侧栏头像按钮协调）

## 2. 前台 HTML 结构

- [x] 2.1 重构 `index.html` 中 `#profileOverlay`：替换 `modal-overlay` / `modal-card` / `login-field` / `btn` 为 Studio class；增加 `#profileAvatarPreview` 容器
- [x] 2.2 重构 `index.html` 中 `#passwordOverlay`：同样替换为 Studio class；保留复杂度提示，使用 `sk-muted` 层级 class
- [x] 2.3 移除弹层 markup 中的内联 `style` 属性，改由 CSS class 控制间距

## 3. 前台脚本

- [x] 3.1 在 `openProfileOverlay()` 中根据 `state.currentUser` 填充头像预览（有 `avatar_url` 显示图片，否则首字母占位，逻辑与 `renderFrontUserSidebar` 一致）
- [x] 3.2 确认 `saveProfile()` / `savePassword()` 保存成功后仍正确关闭弹层并刷新侧栏；上传头像成功后更新预览（若响应含新 `avatar_url`）

## 4. 验收

- [x] 4.1 手动验证：个人资料与修改密码弹层背景/按钮/input focus 与壳内 Studio 区域一致，且不依赖 `login.css`
- [x] 4.2 手动验证：有/无头像时个人资料弹层预览正确；改密复杂度提示可读
- [x] 4.3 回归：用户菜单、退出确认框、歌单模态等既有流程未因本变更破坏
