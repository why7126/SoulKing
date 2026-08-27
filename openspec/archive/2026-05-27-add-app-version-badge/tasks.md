## 1. 版本数据源

- [x] 1.1 在 `app/config.py` 的 `Settings` 中新增 `app_version: str = "0.0.6"`
- [x] 1.2 新增 `app/static/version.js`，导出 `export const APP_VERSION = "v0.0.6"`

## 2. 共享样式

- [x] 2.1 在 `app/static/styles.css` 新增 `.app-brand-title-row` 与 `.app-brand-version`（muted 小字、`JetBrains Mono`、方案 A 角标）
- [x] 2.2 确认收起侧栏时版本角标随 `.sk-brand-text` / `.adm-brand-text` 隐藏，无需额外 CSS

## 3. 前台壳

- [x] 3.1 更新 `app/static/index.html` 品牌区：标题行包裹 `.app-brand-title-row`，内嵌 `<span class="app-brand-version" id="appBrandVersion">`
- [x] 3.2 在 `frontend.js`（或极短 inline module）最早阶段 import `APP_VERSION`，写入角标 `textContent` 与 `aria-label`
- [x] 3.3 （可选）初始化时将 `document.title` 追加版本前缀/后缀，与 `APP_VERSION` 同源

## 4. 后台壳

- [x] 4.1 更新 `app/static/admin.html` 品牌区结构，与前台对称（共用 `.app-brand-version`）
- [x] 4.2 在 `admin.js` 入口同样 import `APP_VERSION` 并渲染角标（可抽共享 `applyAppVersion()` 至 `version.js` 导出）

## 5. 缓存版本与验收

- [x] 5.1 递增 `index.html` / `admin.html` 中 `styles.css`、`studio.css`、`admin-studio.css`、`version.js` 及相关脚本的 `?v=` 缓存参数
- [x] 5.2 目视验收：前台/后台展开态显示相同 `v0.0.6`，收起态角标隐藏
- [x] 5.3 确认角标文案不受样式表 `?v=` 变更影响，仅随 `version.js` 更新
