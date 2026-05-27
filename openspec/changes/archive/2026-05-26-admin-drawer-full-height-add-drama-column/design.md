## Context

后台歌曲管理页使用 `.adm-workspace` 横向 flex 布局：左侧为 `.adm-main-column`（表格 + 分页），右侧为 `#adminEditPanel.admin-edit-panel`。面板已具备 `display: flex; flex-direction: column` 及 `.drawer-body-scroll { flex: 1 }`，但面板自身未显式拉伸至工作区全高，在部分视口下可能出现面板高度短于表格区、底部留白的情况。

编辑抽屉底部现有三个按钮：取消、保存草稿、保存。`saveDraftBtn` 点击后将 `title`、`album`、`release_date`、`duration_ms` 写入 `localStorage`（key `adm-draft-${songId}`），**无**打开抽屉时的读取/合并逻辑，用户无法真正恢复草稿。

`film_tv` 字段：数据库列、列表 API 响应、详情 API、`PATCH` 更新及编辑抽屉 `#filmTvInput` 均已实现；列表表头与 `renderSongs` / 前台 `renderSongRow` 尚未展示该列。

## Goals / Non-Goals

**Goals:**

- 打开编辑抽屉时，面板纵向占满 `.adm-workspace` 全部可用高度。
- 移除「保存草稿」UI 与相关 JS，底部仅保留「取消」与「保存」。
- 前台、后台歌曲列表在「标签」前插入「影视剧」列，数据来自 `film_tv`。
- 后台表头「影视剧」列支持排序（`data-sort="film_tv"`，与 API 一致）。
- 空列表行 `colspan` 与列数保持一致（后台 16 → 含勾选共 16 列？ 当前 15 列不含勾选是14数据列+check=15，加一列变16）。

Actually let me count admin columns:
1. check
2. 歌曲
3. 原唱
4. 作词
5. 作曲
6. 专辑
7. 语言
8. 标签 -> insert 影视剧 before = 8 film_tv, 9 tags
9. 格式
10. 时长
11. 发行日期
12. 元数据
13. 创建时间
14. 更新时间
15. 操作

Currently colspan=15. After adding film_tv, colspan=16.

**Non-Goals:**

- 不改动编辑抽屉内字段布局（影视剧输入框已在抽屉内）。
- 不新增影视剧筛选维度（筛选区已有或可后续单独做）。
- 不清理历史 `localStorage` 中的 `adm-draft-*` 键（可选清理，非必须）。
- 不修改元数据完成度算法是否计入 `film_tv`。

## Decisions

### 1. 抽屉全高：CSS flex 拉伸而非 fixed 定位

**选择**：为 `.admin-edit-panel.is-open` 增加 `align-self: stretch`（或 `height: 100%`），并确认 `.adm-workspace` 父级链具备 `flex: 1; min-height: 0`。`.drawer-form` 设为 `flex: 1; min-height: 0; display: flex; flex-direction: column`，使 `.drawer-body-scroll` 在面板内滚动。

**理由**：与现有内嵌面板架构一致，无需改为 overlay 抽屉；表格区与面板同高，视觉对齐。

**备选**：改为 fixed 全屏 overlay 抽屉 —— 超出本次需求，且与当前「表格旁内嵌编辑」产品形态不符。

### 2. 移除保存草稿：删 HTML + JS，不保留隐藏入口

**选择**：删除 `#saveDraftBtn` 按钮、`els.saveDraftBtn` 引用及 click 监听器；不新增「未保存提示」。

**理由**：功能不完整且无回显；用户应使用「保存」提交服务端。「取消」关闭抽屉行为保持不变。

### 3. 影视剧列：纯展示，复用 API 字段

**选择**：

- 后台：在 `admin.html` 表头 `<th>` 于「语言」与「标签」之间插入 `<button data-sort="film_tv">影视剧</button>`；`renderSongs` 增加 `<td>${escapeHtml(song.film_tv || "—")}</td>`。
- 前台：在 `index.html` 表头于「语言」与「标签」之间插入 `<th class="sk-col-meta">影视剧</th>`；`frontend.js` 行模板在 language 与 tags 之间插入 `film_tv` 单元格。

**理由**：零后端改动；与产品文档列顺序（专辑、影视剧、语言…）略有差异但用户明确要求「标签前面」。

**备选**：将影视剧放在专辑之后 —— 与用户指定顺序不符。

### 4. 列宽与横向滚动

**选择**：影视剧列使用与其他 meta 列相同的 class（前台 `sk-col-meta`）；后台不单独冻结该列。若表格总宽超出容器，沿用 `.adm-table-scroll` 横向滚动。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 新增列挤压窄屏可读性 | meta 列允许文本截断或横向滚动；与现有列行为一致 |
| 移除草稿后用户误关丢失编辑 | 与移除半成品能力一致；正式保存仍走「保存」 |
| colspan 遗漏导致空态表格错位 | 统一搜索 `colspan="15"` 并改为 16 |
| 全高 CSS 与底部播放器叠层 | 抽屉在 `.adm-workspace` 内，播放器在其外；沿用现有 flex 链 |

## Migration Plan

纯前端静态资源变更：更新 HTML/JS/CSS 并递增 `?v=` 缓存参数。无数据库迁移。部署后刷新页面即可。可选：用户本地 `localStorage` 中旧草稿键自然过期，无需服务端处理。

## Open Questions

（无 — 需求已明确。）
