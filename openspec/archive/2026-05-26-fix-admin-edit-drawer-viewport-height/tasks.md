## 1. 抽屉定位与主内容区全高

- [x] 1.1 在 `admin-studio.css` 为 `#admin-page-music .admin-edit-panel.is-open` 设置 `position: fixed; top: 0; right: 0; bottom: var(--adm-player-total-h); width: var(--adm-edit-w); z-index` 等，移除仅适用于 flex 内嵌的 `height: 100%` / `align-self: stretch`
- [x] 1.2 为 `#admin-page-music.is-edit-drawer-open .admin-studio-root`（或等价容器）设置 `margin-right: var(--adm-edit-w)`，打开抽屉时预留宽度
- [x] 1.3 合并/统一 `@media (max-width: 1100px)` 抽屉 fixed 规则，确保 `bottom: var(--adm-player-total-h)` 与桌面一致

## 2. 滚动链与 JS 联动

- [x] 2.1 为 `.admin-edit-panel .drawer-body-scroll` 补充 `min-height: 0`；确认 `.drawer-form` flex 链完整
- [x] 2.2 在 `admin.js` 的 `openEditPanel` / `closeEditPanel` 中为 `#admin-page-music` 切换 `is-edit-drawer-open` 类

## 3. 验收与缓存

- [x] 3.1 手动验证：抽屉从主内容顶到播放器上沿全高；页头/工具栏右侧与抽屉并列不重叠；正文可滚动、底栏固定
- [x] 3.2 手动验证：侧栏折叠、窄屏（≤1100px）下行为正常
- [x] 3.3 递增 `admin.html` 中 `admin-studio.css` / `admin.js` 的 `?v=` 缓存参数
