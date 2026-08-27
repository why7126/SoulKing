---
purpose: 原型驱动 UI 验收标准
content: 带 prototype 的 UI Change 的 UI Contract、Skeleton、截图、computed style、Mock/API 和一致性验收清单
created_at: 2026-08-10 23:20:00
updated_at: 2026-08-10 23:20:00
---

# 原型驱动 UI 验收标准

本标准适用于包含 `prototype/`、`prototype_refs`、`AC-PROTOTYPE-*`、UI Skeleton 或明确引用既有页面视觉的 UI Change。目标是把“像不像原型”前置为可执行合同、截图证据和可复核样式检查。

## UI Contract

`/req-opsx` MUST 在 Change `design.md` 写入 UI Contract。缺少 UI Contract 时，`/opsx-apply` 只能补齐合同和 Skeleton，不得把 UI 实现标记完成。

UI Contract 至少包含：

- 事实源优先级：`prototype.html`、PNG/截图、`context.md`、`acceptance.md`、`ui-design.md`、既有 `app/static/` 页面。
- 页面与入口：路由、导航入口、默认落点、登录态和权限态差异。
- 信息架构：侧边栏、顶部区、主内容、浮层、表格、列表、抽屉、播放器、空态和错误态。
- 视觉 token：字体、字号、行高、颜色、边框、间距、圆角、阴影、层级和滚动规则。
- 交互状态：hover、active、focus、disabled、loading、click outside、展开/收起和键盘可达性。
- Mock/API 边界：Mock 区域、真实 API 区域、后续接入计划、生产风险和验收非目标。

## Skeleton 首轮确认

带 prototype 的 UI Change MUST 先完成 Skeleton，再进入细节实现。Skeleton 至少覆盖页面壳、布局区域、导航结构、用户菜单、弹窗/抽屉容器、主要状态容器、稳定选择器和占位数据边界。

Skeleton 证据未通过时，不得继续关闭细节实现任务。

## 视觉截图门禁

`/opsx-apply` 和 `/opsx-modify` 完成 UI 任务前 MUST 记录 1440px 桌面视口证据。若页面存在关键交互，还 MUST 记录对应交互状态。

必查场景：

- 默认首屏：页面标题、导航、主要区域、间距、对齐、滚动边界、文本溢出。
- 侧边栏和用户菜单：展开、收起、active 态、分组、弹出方向、危险色、遮挡风险。
- 弹窗/抽屉：宽高、层级、背景区分、边框、滚动、底部操作。
- 筛选与列表：输入框、选择控件、空态、错误态、表格密度。
- 播放器和媒体控件：按钮尺寸、图标居中、进度、状态切换和布局稳定性。

## Computed Style

对原型差异风险高或验收反馈已指出的视觉点，MUST 使用浏览器 computed style、Playwright 断言或等价工具记录关键属性。

示例属性包括 `font-family`、`font-size`、`font-weight`、`line-height`、`width`、`height`、`padding`、`margin`、`gap`、`color`、`background-color`、`border-color`、`position`、`z-index`、`overflow`。

## Mock/API 边界

带 UI 的 Change 必须声明数据边界。使用 Mock 数据时，明确 Mock 字段、Mock 来源和不代表真实 API 已完成；使用真实 API 时，明确接口来源、权限、错误态和空态。

## 归档门禁

`/opsx-archive` 前 MUST 复核 linked REQ 与 Change 的 UI Contract、Skeleton、截图、computed style、Mock/API 边界和最终实现一致。缺证据、证据 stale 或边界未声明时，归档应阻断。
