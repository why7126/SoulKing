## MODIFIED Requirements

### Requirement: 后台用户管理界面

后台壳 SHALL 提供「用户管理」导航页，支持列表展示、创建用户、编辑角色与启用状态、软删除、重置密码；页面布局、工具栏、搜索框、表格与底栏视觉 MUST 与后台「歌曲管理」及统一后的艺人/标签/语言管理页采用同一 SoulKing Admin 组件体系（`admin-studio-root`、`adm-toolbar`、`adm-search-wrap`、`adm-data-table` 或等价 Admin 表样式、`adm-table-footer`），不得继续以 Hermes `panel` + `admin-search-row` 作为主结构。列表操作列 MUST 仅展示「更多」（⋮）按钮，切换角色、启用/禁用、重置密码、删除 MUST 位于 `.table-more-menu` 内，不得行内并列多按钮。

#### Scenario: 管理员打开用户管理页

- **GIVEN** 管理员已登录后台壳
- **WHEN** 用户点击侧栏「用户管理」
- **THEN** 主内容区展示用户列表与操作入口
- **AND** 页面呈现与「歌曲管理」一致的 Admin 工具栏与表格容器结构

#### Scenario: 用户管理操作列仅更多按钮

- **GIVEN** 用户管理列表已加载
- **WHEN** 用户查看任意用户行的操作列
- **THEN** 可见控件仅为「更多」（⋮）按钮
- **AND** 行内不存在独立的「角色」「重置密码」「删除」按钮
