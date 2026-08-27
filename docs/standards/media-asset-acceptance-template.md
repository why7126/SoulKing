---
purpose: 音乐媒体资产验收模板
content: 音频、歌词、封面、头像和对象存储链路的 key、object、URL/playback、metadata、UI render 验收记录
created_at: 2026-08-21 22:50:52
updated_at: 2026-08-21 22:50:52
---

# 音乐媒体资产验收模板

## 适用范围

本文用于媒体相关 REQ、BUG、OpenSpec Change、Sprint 验收报告和发布前检查，统一记录音频、歌词、封面、头像和对象存储链路的验收事实。

本模板只定义验收证据结构和记录口径，不新增导入接口、转码、歌词解析、缩略图、对象存储架构、API、数据库、Web 或 Docker Compose 行为。

## 状态与必填规则

每个媒体样例的每个维度必须使用以下状态之一：

| 状态 | 含义 | 必填补充 |
|---|---|---|
| `pass` | 已验收通过，有可复核证据 | 证据摘要、入口或命令摘要 |
| `fail` | 已验收失败 | 失败现象、影响范围、复现入口、期望结果、实际结果和排查线索 |
| `n/a` | 当前 Change 或场景不涉及该维度 | N/A 理由，不得留空 |
| `blocked` | 环境、账号、网络、依赖、数据或设备阻塞 | 阻塞原因、责任环境、重试条件和当前影响判断 |

任一维度为 `fail` 时整体结论不得为 `pass`；任一必验维度为 `blocked` 时整体结论不得为 `pass`。

## 五维检查目标

| 维度 | 检查目标 | 通过标准 | 证据字段 |
|---|---|---|---|
| `key` | 媒体对象标识与业务资源关系 | `object_key` 或等价脱敏标识符合 `soulking` 单桶和前缀策略 | 媒体类型、业务资源、脱敏 key、前缀、关联记录 |
| `object` | 对象存储事实 | object 存在，MIME、大小、安全校验和权限边界符合预期 | 对象存在性、MIME、size、权限结论、对象来源 |
| `URL / playback` | 受控访问、流式播放或下载结果 | presigned URL、后端流式接口、下载接口或页面代理入口可访问；前端不直连未授权对象存储 | URL 类型、HTTP 状态、接口或页面入口、播放/下载结果 |
| `metadata` | 音乐媒体元数据 | 音频指纹、文件大小、格式、时长、歌词格式、封面尺寸或头像类型符合业务预期 | sha256/file_size 摘要、格式、时长、尺寸、关联歌曲或用户 |
| `UI render` | 用户入口渲染 | 前台、后台、登录页或用户资料入口能展示媒体成功态、空态或失败态 | 页面路径、控件、视口或浏览器、展示结论 |

## Markdown 记录模板

| 样例 | 媒体类型 | 业务资源 | key | object | URL / playback | metadata | UI render | 结论 |
|---|---|---|---|---|---|---|---|---|
| sample-001 | audio/lyrics/cover/avatar | 待填写 | pass/fail/n/a/blocked | pass/fail/n/a/blocked | pass/fail/n/a/blocked | pass/fail/n/a/blocked | pass/fail/n/a/blocked | pass/fail/n/a/blocked |

每个非 `pass` 单元格必须在下方补充原因：

```markdown
### sample-001 失败 / N/A / blocked 记录

- key：pass；证据：脱敏 object_key 与歌曲、歌词或用户资源关系一致。
- object：fail；实际结果：对象存储中未找到对应 object；期望结果：object 存在且 MIME、size 符合上传结果；影响范围：歌曲无法播放或封面无法展示；复现入口：后台歌曲详情页刷新。
- URL / playback：blocked；原因：测试对象存储 endpoint 不可访问；责任环境：对象存储服务；重试条件：服务恢复后重新执行播放或下载 smoke。
- metadata：n/a；原因：当前变更只更新头像展示，不涉及音频指纹或歌词格式。
- UI render：pass；证据：后台用户资料页头像已显示，失败态可见。
```

## YAML 记录模板

```yaml
media_asset_acceptance:
  template_ref: docs/standards/media-asset-acceptance-template.md
  target:
    type: change
    id: <change-id>
  samples:
    - id: sample-001
      media_type: audio
      business_resource: "歌曲音频 / 脱敏资源描述"
      key:
        status: pass
        evidence: "脱敏 object_key 符合 soulking 单桶与前缀策略"
      object:
        status: pass
        evidence: "object 存在，MIME 与 size 符合预期"
      url_playback:
        status: pass
        url_type: stream_api
        http_status: 206
        evidence: "用户入口可播放音频，未直连未授权对象存储"
      metadata:
        status: pass
        evidence: "sha256 + file_size 去重摘要与记录一致"
      ui_render:
        status: blocked
        reason: "缺少可用浏览器验收环境"
        retry_condition: "本地服务启动后重新验证播放控件"
      conclusion: blocked
```

## 失败转 BUG 最小信息

任一维度为 `fail` 时，记录必须足以支撑后续 `/bug-capture` 或返修，至少包含：

- 失败现象。
- 影响范围。
- 复现入口。
- 期望结果。
- 实际结果。
- 相关媒体类型、业务资源、脱敏 key 或 URL 摘要。
- 端和环境，例如前台 Web、后台管理端、Docker Web 或发布检查。
- 截图、日志或命令摘要位置；不得粘贴大段日志。

## 安全与证据边界

允许记录：

- 脱敏后的对象 key、相对 URL、代理 URL 摘要或 HTTP 状态。
- 命令与结果摘要。
- 仓库相对路径形式的截图、录屏、报告或人工验收摘要。
- N/A、blocked、失败现象和剩余风险。

禁止记录：

- 真实用户隐私、个人媒体内容、未脱敏文件名或播放地址。
- 真实密钥、AccessKey、SecretKey、数据库 DSN、MinIO 凭据。
- Authorization header、Cookie、`.env` 内容。
- 本机绝对路径、完整敏感请求体、大段日志或不可公开运维地址。
