## ADDED Requirements

### Requirement: 前台播放器 LRC 同步显示

当前台壳正在播放可试听曲目且该曲存在可读取的歌词时，`#playerLyricLine` SHALL 随音频播放进度更新为当前时间对应的歌词行文本。切换播放曲目时，客户端 MUST 重新加载该曲歌词；加载完成前可显示加载中或保留上一曲文案直至更新。

若无歌词或歌词接口返回无歌词，则 `#playerLyricLine` SHALL 显示固定占位文案（如「当前暂无歌词同步显示」）。若有歌词但当前时间点无匹配行，SHALL 显示空行、省略号或上一行文本之一，行为须在实现中一致。

更新歌词 DOM 时 SHOULD 仅在当前行文本变化时写入，以避免不必要的重绘。

#### Scenario: 有 LRC 时随播放进度更新

- **GIVEN** 用户正在前台播放歌曲 S，且 S 有关联 LRC
- **WHEN** 播放进度越过某一歌词行的时间戳
- **THEN** `#playerLyricLine` 显示该行文本

#### Scenario: 切歌后歌词更新

- **GIVEN** 用户从歌曲 A 切换到歌曲 B
- **WHEN** B 开始播放且 B 有 LRC
- **THEN** `#playerLyricLine` 显示 B 的歌词而非 A 的残留文本

#### Scenario: 无 LRC 时显示占位

- **GIVEN** 用户正在播放歌曲 C，且 C 无 LRC
- **WHEN** 播放进行中
- **THEN** `#playerLyricLine` 显示无歌词占位文案

### Requirement: 前台检查器歌词 Tab 内容

前台壳右侧检查器在「歌词」Tab 激活时 SHALL 展示当前选中曲目的歌词全文（原始文本或分行列表）。未选中曲目时 SHALL 提示用户先选择曲目。选中但无 LRC 时 SHALL 说明暂无歌词及可通过扫描侧车或后台上传关联。

Tab 切换 MUST 更新 `inspectorTab` 状态并渲染对应面板内容，不得仅切换按钮高亮而无内容变化。

#### Scenario: 选中曲目后查看歌词 Tab

- **GIVEN** 用户已在列表选中歌曲 D，且 D 有 LRC
- **WHEN** 用户点击检查器「歌词」Tab
- **THEN** 面板中可见 D 的完整歌词内容

#### Scenario: 无歌词时的 Tab 提示

- **GIVEN** 用户已选中歌曲 E，且 E 无 LRC
- **WHEN** 用户打开「歌词」Tab
- **THEN** 面板显示无歌词说明，而非空白无提示

### Requirement: 后台编辑抽屉歌词上传

后台壳歌曲编辑抽屉中的「替换歌词」控件 SHALL 触发文件选择（接受 `.lrc`），并通过歌曲歌词上传接口提交；成功后更新 `#editLyricName` 等展示为当前文件名。失败时 SHALL 以 Toast 或等价方式显示错误，不得仅显示「即将推出」类占位。

#### Scenario: 替换歌词成功

- **GIVEN** 用户打开某曲编辑抽屉
- **WHEN** 用户选择有效 `.lrc` 并确认上传
- **THEN** 界面显示该文件名
- **AND** 该曲可通过歌词读取接口获得新内容

#### Scenario: 上传非 LRC 被拒绝

- **GIVEN** 用户尝试选择非 `.lrc` 文件
- **WHEN** 客户端校验或服务端返回错误
- **THEN** 用户看到可读错误提示且曲库歌词不变

### Requirement: 后台播放器歌词行（可选一致）

后台歌曲管理页底部播放器若存在 `#adminPlayerLyricLine`，在播放可试听曲目时 SHALL 与前台采用相同的歌词加载与同步逻辑；无歌词时 MUST 显示与前台一致的占位文案。

#### Scenario: 后台播放有 LRC 曲目

- **GIVEN** 管理员在后台播放已关联 LRC 的曲目
- **WHEN** 播放进度推进
- **THEN** `#adminPlayerLyricLine` 显示与当前时间匹配的歌词行或占位
