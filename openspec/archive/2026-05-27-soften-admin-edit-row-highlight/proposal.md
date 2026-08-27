## Why

后台歌曲列表在拆分「正在播放」（`is-playing`）与「编辑选中」（`is-active`）后，编辑态 CSS 对每个 `td` 施加了 `box-shadow: inset 3px 0 0`，导致一行出现多条紫色竖线，视觉过重且与前台「弱选中」不一致。需要收紧编辑选中行的样式契约，使其弱于播放行、且仅在最左侧（若有）保留一条指示。

## What Changes

- 调整 `admin-studio.css` 中 `tbody tr.is-active`（编辑选中，非播放）样式：移除各列重复的左侧 inset 阴影；背景使用与前台 `is-selected` 同级的弱对比色。
- 若保留「正在编辑」指示，仅在行首冻结列（如 `.col-check` 或 `.col-title`）施加**一条**左侧 accent，或仅依赖略深背景，不得对中间/右侧每列重复竖条。
- 删除或合并与 `#admin-page-music` 规则冲突的宽泛 `tr.is-active` 旧规则（如 `rgba` 叠层 + `tr` 级 `box-shadow`），避免编辑行双重高亮。
- 播放行 `is-playing` 样式保持不变。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `web-static-client-shells`：细化「后台列表区分正在播放与编辑选中」中编辑选中行的视觉约束（弱于播放、禁止每列竖条、最多左侧一条）。

## Impact

- `app/static/admin-studio.css`（主要）
- 无 API、无 `admin.js` 逻辑变更（除非验收发现 class 误用）
