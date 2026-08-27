---
requirement_id: REQ-0003-web-static-client-shells
title: Web 静态前后台客户端壳
terminal: multi
version: v1
status: archived
owner: product
source: openspec/specs/web-static-client-shells/spec.md
priority: P1
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
parent_requirement:
related_spec: web-static-client-shells
---

# Web 静态前后台客户端壳

## 背景
ProjectSoulKing 当前已在代码与已生效 OpenSpec 中实现 `web-static-client-shells` 能力。为避免需求状态只存在于对话或规格结果中，本需求将该能力回填到 `issues/requirements`，作为可审计的历史需求档案。

## 目标用户
- 个人音乐库维护者
- 管理员
- 已登录普通用户（适用于面向前台或账号自助的能力）

## 用户价值
定义「Web 静态客户端壳」能力：服务端将静态资源目录以固定 URL 前缀对外提供；通过两条入口路径分别交付 **前台壳** 与 **后台壳** 的 HTML 文档；文档内挂载样式表与 **单一 ES 模块脚本入口**，由脚本调用后端接口并驱动界面（前台默认将站内路径拼为同源 URL）。本规范仅描述壳层交付与跨页导航；具体业务（曲库、歌单、扫描等）由其它能力规范覆盖。仓库中另有未接入任一脚本页的静态脚本文件，见 Known Gaps。

## 范围 In
- 覆盖 `web-static-client-shells` 已生效规格中的 66 个 Requirement。
- 以当前代码、OpenSpec 与产品文档描述的已实现行为为准。
- 保留规格中的 Notes 与 Known Gaps 作为后续演进输入。

## 范围 Out
- 不在本需求中新增接口、数据结构、权限边界或 UI 行为。
- 不直接修改 `openspec/specs/`，仅引用其作为已生效事实源。
- 不承诺修复 Known Gaps；后续若处理需另建 REQ/BUG 与 OpenSpec Change。

## 功能要求
- FR-001：静态资源 URL 前缀
- FR-002：前台入口路径
- FR-003：后台入口路径
- FR-004：前台壳的样式与模块脚本
- FR-005：后台壳的样式与模块脚本
- FR-006：前台 API 请求的 URL 组装
- FR-007：后台数据请求的 fetch 路径形态
- FR-008：壳内前后台跳转
- FR-009：后台歌曲管理页快速筛选选项来源
- FR-010：后台歌曲管理页列表表格列与顺序
- FR-011：后台歌曲管理页主区滚动与视口
- FR-012：后台歌曲管理页列表容器双轴滚动
- FR-013：后台歌曲管理页列表操作按钮
- FR-014：后台歌曲管理页表格冻结列
- FR-015：后台歌曲管理页服务端分页与总数展示
- FR-016：后台歌曲管理页快速筛选可搜索多选
- FR-017：可搜索多选筛选控件勾选交互
- FR-018：前台壳侧栏主导航结构
- FR-019：前台壳侧栏未实现导航项禁用态
- FR-020：登录页
- FR-021：API 请求携带会话与 401 处理
- FR-022：侧栏展示真实用户
- FR-023：后台用户管理导航
- FR-024：前台壳侧栏底部用户菜单
- FR-025：前台壳个人资料与修改密码弹层 Studio 视觉
- FR-026：前台个人资料用户名只读展示
- FR-027：前台修改密码二次确认与保存门禁
- FR-028：前台头像展示刷新与 cache-bust
- FR-029：后台壳侧栏底部用户菜单
- FR-030：前台壳侧栏收起与展开
- FR-031：后台壳侧栏收起与展开
- FR-032：前台壳音乐库内容区布局与筛选
- FR-033：前台壳音乐库歌曲列表列定义
- FR-034：前台壳音乐库服务端分页与页脚信息
- FR-035：前台壳音乐库表格冻结列
- FR-036：前台壳底部播放器播放模式选择
- FR-037：Studio 播放器 transport 圆钮图标居中
- FR-038：前台壳未实现占位控件隐藏
- FR-039：前台壳底部播放器紧凑两行布局
- FR-040：前台播放器 LRC 同步显示
- FR-041：前台播放器歌词行显示切换
- FR-042：前台检查器歌词 Tab 内容
- FR-043：后台编辑抽屉歌词上传
- FR-044：后台播放器歌词行（可选一致）
- FR-045：后台歌曲管理页编辑抽屉宽度
- FR-046：后台歌曲管理页编辑抽屉原唱作词作曲字段
- FR-047：后台歌曲管理页编辑抽屉标签多选
- FR-048：后台歌曲管理页编辑抽屉风格字段
- FR-049：后台歌曲管理页编辑抽屉格式只读聚合
- FR-050：后台歌曲管理页编辑抽屉多选选项列表对齐
- FR-051：后台歌曲管理页列表操作列仅更多下拉
- FR-052：后台歌曲管理页编辑抽屉影视剧字段
- FR-053：后台歌曲管理页编辑抽屉发行日期选择器
- FR-054：后台歌曲管理页编辑抽屉主内容区全高布局
- FR-055：后台歌曲管理页编辑抽屉无保存草稿
- FR-056：后台歌曲管理页编辑抽屉可编辑时长
- FR-057：后台歌曲管理页 Studio 风格底部播放器
- FR-058：前台曲库与歌单详情列表中当前播放行可见且不被子表头遮挡
- FR-059：前台与服务端分页一致时切歌自动翻到含曲页
- FR-060：后台列表区分正在播放与编辑选中且播放态与前台一致
- FR-061：后台切歌跨页时自动加载正确页
- FR-062：壳层产品版本角标
- FR-063：产品版本发版维护约定
- FR-064：后台参考数据管理页 Admin 布局一致性
- FR-065：后台用户管理页 Admin 布局一致性
- FR-066：后台参考数据管理页操作列仅更多下拉

## UI 约束
- 涉及前台或后台壳的能力，遵守 `ui-design.md` 与 `rules/ui-design.md` 的既有要求。
- 非 UI 能力不新增界面约束，以对应 OpenSpec 说明为准。

## 关联需求
- 关联规格：`openspec/specs/web-static-client-shells/spec.md`
- 关联归档 Change：
- `2026-05-22-fix-admin-song-filter-multiselect`
- `2026-05-23-fix-admin-song-list-internal-scroll`
- `2026-05-23-fix-admin-song-list-layout-footer`
- `2026-05-23-fix-admin-song-management-ux`
- `2026-05-23-fix-front-user-menu-dismiss`
- `2026-05-23-optimize-admin-song-filter-option-sources`
- `2026-05-23-optimize-admin-song-list-columns-pagination`
- `2026-05-23-optimize-front-layout-nav`
- `2026-05-24-add-sidebar-collapse-toggle`
- `2026-05-24-admin-song-list-freeze-columns`
- `2026-05-24-fix-admin-edit-drawer-multiselect-alignment`
- `2026-05-24-optimize-admin-song-edit-drawer`
- `2026-05-24-optimize-frontend-library`
- `2026-05-24-optimize-frontend-library-content`
- `2026-05-24-optimize-frontend-library-list`
- `2026-05-24-optimize-frontend-library-player`
- `2026-05-25-optimize-admin-song-management-page`
- `2026-05-26-add-lyrics-support`
- `2026-05-26-admin-drawer-full-height-add-drama-column`
- `2026-05-26-fix-admin-edit-drawer-viewport-height`
- `2026-05-26-optimize-frontend-player-lyrics`
- `2026-05-27-add-app-version-badge`
- `2026-05-27-add-song-list-genre-column-filter`
- `2026-05-27-fix-searchable-filter-checkbox-interaction`
- `2026-05-27-fix-song-list-playing-highlight-scroll-transport`
- `2026-05-27-fix-studio-transport-icon-centering`
- `2026-05-27-soften-admin-edit-row-highlight`
- `2026-05-27-sync-title-filenames-editable-duration`
- `2026-05-28-add-user-auth-system`
- `2026-05-28-align-profile-password-ui-with-studio-design`
- `2026-05-28-align-user-menu-logout-ux`
- `2026-05-28-fix-profile-avatar-password-ux`
- `2026-05-29-add-password-show-hide-toggle`
- `2026-05-29-align-admin-metadata-pages-ui`
- `2026-05-29-align-user-menu-logout-ux`
- `2026-05-29-fix-avatar-presigned-display`

## Notes
- 前台与后台壳内存在大量业务控件与区域显隐；子视图多数由脚本内存状态驱动，**不**依赖浏览器地址栏路径片段区分（与采用 History 路由的单页应用不同）。
- 样式表与脚本链接上的版本查询参数（如 `?v=`）仅用于缓存刷新，数值随发布变更，不作为对外契约字段。
- 当前服务端实现中：静态资源挂载前缀为 `/static`，站点根路径为 `/`，管理入口路径为 `/admin`；若反向代理改写前缀，以部署为准。
- 前台模块内 **唯一** 封装的数据请求入口会转发至浏览器网络请求；模块脚本文件本身仍可再拆分或由运行时加载其它片段，但 HTML 仅声明一条模块脚本入口。

## Known Gaps
- **未挂载脚本**：静态目录中存在额外的客户端脚本文件（如 `app.js`），**未被**前台或后台 HTML 引用；是否仍供手工或其它构建流程使用，本规范不承诺。
- **壳内占位与装饰**：部分主导航或分层 Tab 在界面中呈禁用或静态文案（如「暂未开发」、示意存储用量），其与服务端数据的一致性未在壳层规范中定义为实时接口驱动。
- **第三方字体**：壳文档依赖公网字体样式表；离线或受限网络下的降级表现取决于浏览器，未在代码中单独处理。
- **入口文件缺失或不可读**：若静态目录中缺少 `index.html` / `admin.html` 或进程无读取权限，对应入口路由可能返回错误响应；具体状态码与正文依赖服务端与部署，未在壳层单独约定。

## 状态
- 当前状态：`archived`
- 归档原因：已实现能力的需求资产回填。
