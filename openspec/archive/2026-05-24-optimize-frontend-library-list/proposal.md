## Why

前台音乐库列表已实现左右双侧冻结列，但横向滚动时中间列内容会「透出」到冻结列下方，造成文字与按钮重叠，影响扫读；操作列同时展示播放、加入歌单、下载、更多四个图标按钮，占用冻结列宽度且视觉拥挤。需要在不改变 API 的前提下修复冻结列叠层问题，并将次要操作收入「更多」下拉菜单以简化操作列。

## What Changes

- **修复冻结列叠层透底**：音乐库表格（`.studio-library-table`）在横向滚动时，左侧 `#`/`歌曲` 与右侧 `操作` 冻结列 MUST 完全遮挡其下方的滚动列内容，不出现文字或控件重叠；对齐后台歌曲管理页已验证的 `border-collapse: separate` + z-index 分层方案。
- **操作列收拢为「更多」菜单**：音乐库列表操作列默认仅展示「更多」（⋯）按钮；试听、加入歌单、下载移入该按钮触发的下拉菜单，保留既有权限/禁用逻辑（无网页试听时对应项 disabled 并带提示）。
- **下拉菜单交互**：点击「更多」展开/收起行内菜单；点击菜单项触发原有 `play` / `add` / `download` 行为；点击表格外或打开另一行菜单时关闭当前菜单；菜单在 sticky/overflow 容器内使用 fixed 定位避免被裁剪（参考后台 `table-more-menu-fixed` 模式）。
- **收窄操作列宽度**：操作列由四按钮布局改为单按钮 + 菜单后，相应减小 `--sk-lib-sticky-actions-width`。
- 递增 `index.html` / `frontend.js` / `studio.css` 静态资源 `?v=` 缓存版本。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：前台音乐库操作列改为「更多」下拉收纳试听/加入歌单/下载；冻结列横向滚动时不透底、不重叠的验收场景。

## Impact

- **前端**：`app/static/studio.css`（冻结列 z-index/背景/表格 border-collapse 覆盖、操作列宽度、行内下拉菜单样式）、`app/static/frontend.js`（`songRowInnerHtml` 操作列 DOM、菜单展开/关闭与事件绑定）、`app/static/index.html`（缓存版本）。
- **后端 / API**：无变更。
- **范围**：仅 `#songBrowseSection` 音乐库曲库表；歌单详情列表（`songRowPlaylistDetailInnerHtml`）不在本变更范围。
