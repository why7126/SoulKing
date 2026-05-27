## ADDED Requirements

### Requirement: 后台歌曲管理页编辑抽屉多选选项列表对齐

编辑抽屉内原唱、作词、作曲、语言、标签等字段使用的 `multi-select` 下拉菜单中，选项行（含 checkbox 与名称文案）MUST 保持整齐对齐：checkbox MUST 为固定小尺寸控件，不得被编辑抽屉内针对文本输入框的样式（如 `width: 100%`、大 padding、边框背景）拉伸或挤占整行。提示行（`multi-select-meta-hint`）、新建行（`multi-select-meta-row`）与勾选项行（`artist-option`）的左内边距 MUST 视觉一致。在 `.adm-form-grid-3` 等窄列布局中，下拉菜单 MUST 保持可读（如设置合理 `min-width` 或允许菜单相对触发器向右展开），不得因列宽约 150px 导致选项严重错位不可读。

#### Scenario: 选项行 checkbox 与名称同一行左对齐

- **GIVEN** 用户打开编辑抽屉并展开任一元数据多选（如原唱、标签）
- **WHEN** 下拉列表展示若干可勾选项
- **THEN** 每行 checkbox 宽度约为标准复选框尺寸（约 16px），不与行宽同宽
- **AND** 名称文案紧邻 checkbox 右侧同一行显示
- **AND** 各行 checkbox 左缘垂直对齐

#### Scenario: 三列艺人字段下拉可读

- **GIVEN** 编辑抽屉处于打开状态且原唱、作词、作曲位于三列网格中
- **WHEN** 用户展开任一职艺人多选下拉
- **THEN** 下拉菜单宽度不小于 200px（或等价 min-width）
- **AND** 选项列表不出现 checkbox 被拉满整行导致文字不可读的情况

#### Scenario: 搜索框仍保持全宽

- **GIVEN** 用户展开语言或标签多选下拉
- **WHEN** 用户查看搜索输入框
- **THEN** 搜索框仍占满菜单内容区宽度
- **AND** 搜索框样式与抽屉内其它文本输入框一致（非 checkbox）
