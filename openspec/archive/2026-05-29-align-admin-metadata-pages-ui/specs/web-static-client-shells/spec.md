## ADDED Requirements

### Requirement: 后台参考数据管理页 Admin 布局一致性

后台壳内「艺人管理」「标签管理」「语言管理」三个主内容区（`#admin-page-people`、`#admin-page-tags`、`#admin-page-language`）SHALL 使用与「歌曲管理」相同的 SoulKing Admin 页面骨架：`admin-studio-root` 根容器、`adm-page-header` 页头（标题与可选描述，无内联 style 覆盖边框/内边距）、`adm-controls` 工具栏区（含 `adm-toolbar` 与 `adm-search-wrap`）、`adm-table-scroll` 表格外层滚动容器，以及 `adm-table-footer` 底栏展示总条数。

各页工具栏 MUST 包含：带搜索图标的 `adm-search-wrap` 搜索输入（艺人/标签/语言分别对应现有搜索字段 id）、清空按钮（有输入时可见）、主操作 `btn-adm-primary`（新建）、以及在有行选中时显示的批量删除控件（使用 Admin 危险样式，不得使用 Hermes 全局 `btn danger` 作为唯一样式）。

各页数据表格 MUST 使用 Admin 数据表样式（与歌曲表共享表头/行/空状态视觉，类名可为 `adm-data-table` 或与 `adm-songs-table` 并列的等价选择器），表头排序控件视觉 MUST 与歌曲列表 `sort-btn` 一致（允许保留 `manager-sort-btn` 类名与 `data-manager` / `data-sort` 属性供脚本使用）。

艺人、标签、语言列表底栏 SHOULD 提供与歌曲管理一致的 `adm-pagination` 客户端分页（默认每页 20 条，可选 50/100），除非该页数据量固定极少且产品明确仅展示总数；至少 MUST 显示「共 N 条」类总数字样（`adm-list-total`）。

#### Scenario: 艺人管理页呈现 Admin 工具栏与搜索框

- **GIVEN** 管理员已登录并打开后台壳
- **WHEN** 用户进入「艺人管理」主内容区
- **THEN** 页面使用 `admin-studio-root` 布局
- **AND** 工具栏包含 `adm-search-wrap` 结构的搜索框（非仅 `search-field-wrap` 平铺输入）
- **AND** 存在 `btn-adm-primary` 的「新建艺人」按钮

#### Scenario: 标签管理表头排序样式与歌曲表一致

- **GIVEN** 用户位于「标签管理」页且表格已渲染
- **WHEN** 用户查看表头「标签名称」排序按钮
- **THEN** 该按钮呈现与歌曲管理列表表头排序控件相同的 Admin 样式（颜色、hover、排序指示）
- **AND** 点击后仍按现有 `manager-sort-btn` 逻辑排序标签列表

#### Scenario: 语言管理底栏展示总条数

- **GIVEN** 语言管理列表已加载且共有 M 条语言
- **WHEN** 用户查看表格下方底栏
- **THEN** 底栏包含 `adm-table-footer` 结构
- **AND** 可见文案表明列表总条数为 M（如「共 M 条」）

#### Scenario: 批量删除按钮使用 Admin 危险样式

- **GIVEN** 用户在艺人管理页勾选至少一行
- **WHEN** 批量删除按钮变为可见
- **THEN** 该按钮使用 `btn-adm-*` 体系下的危险/ghost 组合样式
- **AND** 按钮不具有仅依赖 Hermes `btn danger` 的默认灰红主按钮外观

### Requirement: 后台用户管理页 Admin 布局一致性

后台壳内「用户管理」主内容区（`#admin-page-users`）SHALL 使用与「歌曲管理」及上述参考数据管理页相同的 SoulKing Admin 页面骨架（`admin-studio-root`、`adm-page-header`、`adm-controls`、`adm-search-wrap`、`adm-table-scroll`、`adm-table-footer`）。

用户管理工具栏 MUST 包含 `adm-search-wrap` 搜索框，支持按用户名或昵称进行客户端过滤（大小写不敏感子串匹配）；MUST 包含 `btn-adm-primary` 的「新建用户」按钮。用户列表表格 MUST 使用与其它 Admin 数据表一致的样式。底栏 MUST 展示用户总条数，并 SHOULD 提供与其它管理页一致的客户端分页控件。

#### Scenario: 用户管理页含搜索框

- **GIVEN** 管理员位于「用户管理」页且列表中存在用户名为 `alice`、昵称为 `Alice` 的账号
- **WHEN** 用户在 `adm-search-wrap` 搜索框输入 `ali`
- **THEN** 列表仅展示用户名或昵称匹配该关键字的用户

#### Scenario: 用户管理页布局与歌曲管理同属 Admin 体系

- **GIVEN** 管理员依次打开「歌曲管理」与「用户管理」
- **WHEN** 对比两页的工具栏与表格外层容器
- **THEN** 两页均使用 `adm-toolbar` 与 `adm-table-scroll` 结构
- **AND** 用户管理页不存在仅依赖 `admin-subpage-wrap` + Hermes `panel` 作为主布局的旧模式

### Requirement: 后台参考数据管理页操作列仅更多下拉

艺人、标签、语言、用户四个管理页的表格操作列（`.col-actions`）MUST 与歌曲管理页一致：默认仅展示一个「更多」（⋮）触发按钮（`adm-icon-btn table-more-btn`）；行内 MUST NOT 并列展示「修改」「删除」等独立按钮。各页原有行级操作 MUST 全部移入 `.table-more-menu` 下拉内，并使用与歌曲管理相同的 `menu-btn` 文案与危险项样式（删除为 `danger-text`）。操作列单元格背景与右侧 sticky 行为 MUST 与歌曲管理操作列一致（`--adm-sticky-bg`、hover 时 `--adm-sticky-bg-hover`、右侧阴影）。

艺人/标签/语言菜单 MUST 至少包含「✎ 编辑」「🗑 删除」。用户管理菜单 MUST 包含切换角色、启用/禁用（超管账号无禁用项时省略）、重置密码、删除等现有能力，均通过菜单项触发。

下拉展开逻辑 MUST 复用与歌曲列表相同的 fixed 定位菜单（`table-more-menu-fixed` 挂到 `document.body`），点击外部或其它行「更多」时关闭。

#### Scenario: 参考数据页操作列仅显示更多按钮

- **GIVEN** 管理员位于「标签管理」页且列表已加载
- **WHEN** 用户查看任意数据行的操作列
- **THEN** 可见控件仅为「更多」（⋮）按钮
- **AND** 不存在行内并列的「修改」「删除」文字按钮

#### Scenario: 从更多菜单编辑艺人

- **GIVEN** 用户在「艺人管理」页展开某行更多菜单
- **WHEN** 用户点击「✎ 编辑」
- **THEN** 系统打开与该艺人等价的编辑/新建弹层（现有 `openCreateModal("person", …)` 流程）
- **AND** 菜单关闭

#### Scenario: 用户管理从更多菜单重置密码

- **GIVEN** 用户在「用户管理」页展开某行更多菜单
- **WHEN** 用户点击「重置密码」
- **THEN** 系统触发与变更前相同的重置密码确认与 API 流程
- **AND** 菜单在操作开始前关闭
