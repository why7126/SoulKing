## ADDED Requirements

### Requirement: Studio 播放器 transport 圆钮图标居中

前台壳（`.front-app`）与后台歌曲管理页（`#adminStudioPlayer`）底部播放器 `.studio-transport` 内的上一首、播放/暂停、下一首圆钮，其内部图标（⏮、▶、⏸、⏭）MUST 在圆钮边框盒内几何居中显示。

实现上 MUST 覆盖全局 `styles.css` 对 `button` 的默认 `padding`，使圆钮内容区与 `display: grid; place-items: center`（或等价居中方式）一致；圆钮的固定宽高（切歌约 34×34px、播放/暂停约 40×40px）与现有视觉样式（边框、渐变播放键）MUST 保持不变。

播放/暂停在播放态（▶）与暂停态（⏸）切换时，两种字符 MUST 均保持在各自圆钮内居中，不得因切换产生明显偏向一侧的位移。

#### Scenario: 前台圆钮内图标居中

- **GIVEN** 用户打开前台壳并查看底部播放器 transport 区域
- **WHEN** 用户观察上一首、播放/暂停、下一首三个圆钮
- **THEN** ⏮、▶（或 ⏸）、⏭ 各自位于对应圆钮的几何中心
- **AND** 图标不因圆钮内边距不对称而贴边或偏上/偏下

#### Scenario: 后台圆钮内图标居中

- **GIVEN** 管理员在后台歌曲管理页查看 `#adminStudioPlayer` transport 区域
- **WHEN** 用户观察上一首、播放/暂停、下一首三个圆钮
- **THEN** 图标居中表现与前台 transport 圆钮一致

#### Scenario: 播放与暂停态切换后仍居中

- **GIVEN** 当前正在播放可试听曲目
- **WHEN** 用户点击播放/暂停按钮使图标在 ▶ 与 ⏸ 间切换
- **THEN** 两种状态下图标均保持在播放圆钮内居中
- **AND** 不出现因 padding 导致的明显横向或纵向偏移
