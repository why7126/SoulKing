## ADDED Requirements

### Requirement: 前台播放器歌词行显示切换

前台壳底部播放器控制行中的「词」按钮（`#playerLyricsToggleBtn` 或等效稳定选择器）SHALL 切换第二行歌词区域（`.studio-player-row--lyrics`）的显示与隐藏。

- 默认状态 SHALL 为 **显示** 歌词行（与改版前行为一致）。
- 隐藏歌词行时，播放器总高度 MUST 收缩为仅控制行高度；主内容滚动区域的底部留白 MUST 同步减小，确保列表末行不被遮挡。
- 按钮 MUST 暴露可访问性状态：`aria-pressed` 在显示时为 `true`，隐藏时为 `false`；SHOULD 在激活态有视觉区分（如 `.is-active`）。
- 用户的显示/隐藏偏好 SHOULD 持久化于 `localStorage`（键名由实现固定），刷新页面后恢复上次选择。
- 隐藏歌词行时，客户端 MAY 继续加载与维护 LRC 同步状态；再次显示时 SHOULD 立即呈现当前行文本，无需重新请求。

#### Scenario: 点击按钮隐藏歌词行

- **GIVEN** 用户打开前台壳且歌词行当前可见
- **WHEN** 用户点击「词」按钮一次
- **THEN** `.studio-player-row--lyrics` 不可见
- **AND** 播放器占用高度小于显示歌词行时的高度
- **AND** 「词」按钮 `aria-pressed` 为 `false`

#### Scenario: 再次点击显示歌词行

- **GIVEN** 歌词行已被隐藏
- **WHEN** 用户再次点击「词」按钮
- **THEN** `.studio-player-row--lyrics` 可见
- **AND** `#playerLyricLine` 显示当前曲目歌词或占位文案
- **AND** 「词」按钮 `aria-pressed` 为 `true`

#### Scenario: 刷新后恢复偏好

- **GIVEN** 用户曾将歌词行设为隐藏且偏好已写入 `localStorage`
- **WHEN** 用户刷新页面并再次打开前台壳
- **THEN** 歌词行初始为隐藏状态
- **AND** 主内容区底部留白与隐藏态播放器高度一致

#### Scenario: 隐藏态下列表末行可见

- **GIVEN** 歌词行处于隐藏状态且用户处于音乐库列表视图
- **WHEN** 用户滚动至列表最后一行
- **THEN** 最后一行完整可见于播放器上缘之上
