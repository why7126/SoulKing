## Why

后台歌曲管理页列数较多，横向滚动时用户需要持续对照「勾选 + 歌曲名」与右侧操作按钮。当前仅冻结勾选列与操作列，「歌曲」列会随中间列一起滚出视口；且横向滚动时中间列文字会透出到左右冻结列下方，造成叠字与误读。前台音乐库已验证双侧冻结 + 不透底方案，后台应对齐同等体验。

## What Changes

- **左侧冻结前两列**：勾选列与「歌曲」列在用户横向滚动时 MUST 保持固定在列表滚动容器左侧；表头与数据行同步冻结。
- **修复冻结列透底**：横向滚动至任意位置时，左右冻结列 MUST 完全遮挡下方中间列文字与控件，不出现重叠或「透出」。
- **行态背景一致性**：hover、选中（`is-active`）态下冻结列单元格背景与整行视觉一致，且保持不透明。
- 递增 `admin.html` / `admin-studio.css` 静态资源 `?v=` 缓存版本（若 HTML 引用版本号）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：新增「后台歌曲管理页表格冻结列」要求；补充左侧勾选 + 歌曲双列冻结、横向滚动不透底、行态背景等验收场景。

## Impact

- **前端**：`app/static/admin.html`（为「歌曲」列 th/td 增加 `col-title` 类）、`app/static/admin-studio.css`（主改动：sticky left 第二列、z-index 分层、实色背景、行态 td 背景）、`app/static/admin.js`（渲染歌曲列 td 时添加 `col-title` 类）。
- **后端 / API**：无变更。
- **OpenSpec**：`openspec/specs/web-static-client-shells/spec.md` 增量。
