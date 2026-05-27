## ADDED Requirements

### Requirement: 壳层产品版本角标

前台壳与后台壳侧栏品牌区 SHALL 在品牌标题「SoulKing」旁展示当前**产品版本**角标（方案 A：标题右侧小字 badge，使用 muted 次级色与等宽字体风格）。前台与后台 MUST 展示**相同**版本字符串，该值 MUST 自共享前端模块 `app/static/version.js` 的 `APP_VERSION` 常量读取并写入 DOM，不得在 HTML 中硬编码不同版本。

后端配置 `app/config.py` 的 `Settings.app_version` SHALL 存储与前端语义对应的版本号（发版时与 `version.js` 由开发者手工同步更新）。样式表与脚本链接上的 `?v=` 查询参数 MUST NOT 作为产品版本展示来源。

版本角标 MUST 提供可访问性文本（如 `aria-label="版本 v0.0.6"` 或对辅助技术可见的等价标记）。侧栏处于**收起**态时，版本角标 MUST 随品牌文案区一并隐藏（默认行为，不单独展示于 Logo 下）。

#### Scenario: 前台展开态展示版本角标

- **GIVEN** 用户已打开前台壳且侧栏处于展开态
- **WHEN** 页面加载完成
- **THEN** 侧栏品牌标题「SoulKing」旁可见与 `APP_VERSION` 一致的版本角标
- **AND** 角标视觉为次级 muted 小字 badge，与后台一致

#### Scenario: 后台展开态展示相同版本

- **GIVEN** 用户已打开后台壳且侧栏处于展开态
- **WHEN** 页面加载完成
- **THEN** 侧栏品牌标题旁可见的版本角标与前台 `APP_VERSION` 相同

#### Scenario: 收起侧栏时隐藏版本角标

- **GIVEN** 用户已打开前台或后台壳且侧栏处于展开态并可见版本角标
- **WHEN** 用户点击折叠切换控件收起侧栏
- **THEN** 版本角标不可见
- **AND** 品牌标题与副标题一并不可见

#### Scenario: 版本与静态资源缓存参数区分

- **GIVEN** 开发者将 `index.html` 中某样式表 `?v=` 参数改为新整数
- **WHEN** 用户刷新页面
- **THEN** 产品版本角标仍仅反映 `version.js` 中的 `APP_VERSION`
- **AND** 不因 `?v=` 变更而自动改变角标文案

### Requirement: 产品版本发版维护约定

发版时开发者 MUST 手工同步更新以下位置的版本信息：`app/config.py` 的 `app_version`、`app/static/version.js` 的 `APP_VERSION`，以及迭代文档 `iterations/release_list.md` 中新版本段落（变更说明）。`config.py` 与 `version.js` 的版本语义 MUST 保持一致（允许 `config.py` 无 `v` 前缀而 UI 带 `v` 前缀的格式差异，但数字部分 MUST 相同）。

#### Scenario: 发版后前后台版本一致

- **GIVEN** 开发者将 `APP_VERSION` 更新为 `v0.0.7` 且 `app_version` 更新为 `0.0.7`
- **WHEN** 用户分别打开前台壳与后台壳（侧栏展开）
- **THEN** 两处角标均显示 `v0.0.7`
