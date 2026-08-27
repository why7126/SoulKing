## ADDED Requirements

### Requirement: 后台歌曲管理页编辑抽屉主内容区全高布局

后台壳内歌曲管理页右侧编辑面板（`#adminEditPanel` / `.admin-edit-panel`）在打开状态（`.is-open`）时 MUST 纵向占满**右侧主内容区**可用高度：顶边与主内容区顶边（视口 `top: 0`）对齐，底边与固定底部播放器上沿对齐（`bottom: var(--adm-player-total-h)` 或等价计算）。高度语义 MUST NOT 仅限 `.adm-workspace` 表格行区域。

面板 MUST 采用纵向 flex：`.drawer-head` 与 `.drawer-footer` 不随正文滚动；`.drawer-body-scroll` MUST 占据剩余高度并在溢出时内部纵向滚动（含 `min-height: 0` 约束）。

抽屉打开时，主内容（页头、工具栏、表格区）MUST 在右侧预留与抽屉等宽的布局空间（如 `margin-right: var(--adm-edit-w)`），避免列表被抽屉遮挡。抽屉 MUST NOT 覆盖左侧导航侧栏。

#### Scenario: 抽屉与主内容区同高

- **GIVEN** 用户在歌曲管理页打开某首歌曲的编辑抽屉
- **WHEN** 面板处于 `.is-open` 状态
- **THEN** 抽屉从视口顶边延伸至固定播放器上沿
- **AND** 抽屉高度大于仅含表格的 `.adm-workspace` 区域（覆盖页头/工具栏对应的右侧纵向空间）

#### Scenario: 长表单内部滚动且底栏固定

- **GIVEN** 编辑抽屉已打开且元数据与音频文件列表总高度超出面板可视区
- **WHEN** 用户在抽屉正文区域滚动
- **THEN** 仅 `.drawer-body-scroll` 滚动
- **AND** 抽屉标题栏与底部「取消」「保存」按钮保持可见

#### Scenario: 打开抽屉时主内容不被遮挡

- **GIVEN** 用户打开编辑抽屉
- **WHEN** 用户查看左侧页头、工具栏与歌曲表格
- **THEN** 上述区域不被抽屉覆盖
- **AND** 表格与分页仍可完整交互（右侧留出抽屉宽度）

#### Scenario: 侧栏折叠时抽屉仍贴主内容区右缘

- **GIVEN** 用户折叠后台侧栏后打开编辑抽屉
- **WHEN** 面板处于打开状态
- **THEN** 抽屉右缘贴视口右缘、左缘不侵入侧栏区域
- **AND** 底边仍对齐播放器上沿
