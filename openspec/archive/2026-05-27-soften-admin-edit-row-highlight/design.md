## Context

`fix-song-list-playing-highlight-scroll-transport` 已为后台引入 `is-playing` / `is-active` 双 class。当前 `#admin-page-music .adm-songs-table tbody tr.is-active td` 对**每个**单元格设置 `box-shadow: inset 3px 0 0 var(--adm-accent)`，叠加另一条 `tr.is-active:not(.is-playing)` 的 `rgba` 背景与 `tr` 级 inset 阴影，造成「每列一条紫线」。

前台参考：`.studio-library-table tbody tr.is-selected:not(.is-active) td` 仅换 `--sk-lib-sticky-bg-selected` 背景，无 per-td 竖条。

## Goals / Non-Goals

**Goals:**

- 编辑选中行视觉明显弱于 `is-playing`。
- 任意数据列上不得出现重复的紫色竖条。
- 可选：在最左冻结列（`.col-check`）保留单条 3px accent，或完全无竖条、仅背景区分。

**Non-Goals:**

- 不改播放行、不改前台列表。
- 不改编辑抽屉或 `activeSongId` 逻辑。

## Decisions

1. **方案 A（推荐，与 explore 结论一致）**  
   - 从 `tr.is-active td` 移除全部 `box-shadow`。  
   - 仅保留 `--adm-sticky-bg-selected`（`#181924`，与现有一致）作为行背景。  
   - 删除 `.admin-app .adm-songs-table tbody tr.is-active:not(.is-playing)` 上的 `box-shadow` 与半透明 `rgba` 背景（与 `#admin-page-music` 规则重复且加重）。

2. **可选左侧指示（若产品希望保留「正在编辑」）**  
   - 仅：`tr.is-active:not(.is-playing) td.col-check { box-shadow: inset 3px 0 0 var(--adm-accent); }`  
   - 不在 `.col-title` 及其它列重复。

3. **优先级**  
   - `is-playing` 与 `is-active` 同行时仅 `is-playing` 样式（现有 JS 已保证）。

## Risks / Trade-offs

- **[Risk] 编辑行与 hover 难以区分** → hover 仍用 `--adm-sticky-bg-hover`，选中用 `--adm-sticky-bg-selected`，对比度足够。  
- **[Risk] 无竖条后编辑行不够显眼** → 仍比默认行深；播放行更强紫底。

## Migration Plan

纯 CSS 发布；无数据迁移。

## Open Questions

（无；用户已确认：更弱、不要每列竖条、最多左侧一条或略深背景——实现采用「略深背景 + 可选仅 col-check 一条」。）
