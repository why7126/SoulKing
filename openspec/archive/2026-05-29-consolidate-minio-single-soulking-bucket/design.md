## Context

- 应用通过 `S3Storage`（boto3）访问 MinIO；`Settings.s3_bucket_music` 默认 `music-files`，`s3_bucket_covers` 默认 `music-covers`。
- `ensure_buckets()` 会创建上述两个桶；实际上传、presign、流式读取、删除、桶内复制均只使用 `s3_bucket_music`。
- `music-covers` 仅在配置与建桶逻辑中存在，封面业务尚未写入对象键；前端封面多为 CSS 渐变占位。
- 音频与歌词对象键由 `compute_music_object_key` 等规则生成，存于音乐桶根路径下分层目录；头像键为 `avatar/{user_id}.{ext}`。

## Goals / Non-Goals

**Goals:**

- 全项目仅一个 MinIO 桶：`soulking`（可通过 `S3_BUCKET_MUSIC` 覆盖，但不再支持第二桶配置）。
- 将 `music-files` 桶内对象迁移至 `soulking`（对象键保持不变，避免改库）。
- 将 `music-covers` 桶内对象迁移至 `soulking` 下 `covers/` 前缀（键映射：`covers/{原键}`，若原键已含路径则保留相对结构）。
- 更新代码、环境示例与 OpenSpec；提供迁移脚本供本地/部署环境执行。
- 迁移后删除 `music-files`、`music-covers` 空桶。

**Non-Goals:**

- 本变更不实现歌曲封面 UI 与数据库 `cover_object_key` 业务（仅完成存储布局与迁移）。
- 不改变音频对象键计算规则（除桶名外）。
- 不支持多租户或多桶隔离。

## Decisions

### 1. 配置：保留 `S3_BUCKET_MUSIC`，删除 `S3_BUCKET_COVERS`

- **选择**：`s3_bucket_music` 默认值改为 `soulking`；移除 `s3_bucket_covers` 及 `.env` 中 `S3_BUCKET_COVERS`。
- **理由**：现有代码路径已全部绑定 `s3_bucket_music`；改名桶即可，无需引入新变量名。
- **备选**：新增 `S3_BUCKET=soulking` 并废弃 `S3_BUCKET_MUSIC` —— 改动面更大，收益有限。

### 2. MinIO 迁移：`music-files` → `soulking`（同键复制 + 删旧桶）

MinIO/S3 无原地「重命名桶」；采用：

1. 若不存在则创建 `soulking`。
2. 列出 `music-files` 全部对象，`CopyObject` 到 `soulking`（相同 `Key`）。
3. 验证对象数量/抽样校验后，删除 `music-files` 内对象并 `DeleteBucket`。
4. 对 `music-covers`：每个对象 `Key` 复制到 `soulking`，目标键为 `covers/{Key}`（`Key` 不以 `covers/` 开头时加前缀；若源键已以 `covers/` 开头则不再重复加层）。
5. 清空并删除 `music-covers` 桶。

脚本位置建议：`scripts/migrate_minio_to_soulking.py`（boto3，读取 `.env` 端点与凭证），或文档化 `mc` 命令；实现阶段二选一或两者皆提供。

### 3. 应用与迁移顺序

1. **先跑迁移脚本**（服务可停或只读），确保 `soulking` 含全部数据。
2. **部署新配置**（`S3_BUCKET_MUSIC=soulking`），`ensure_buckets` 仅创建/校验 `soulking`。
3. **删除旧桶**（脚本末尾或人工确认）。

若先部署新代码而未迁移，会因桶内无对象导致播放/头像 404——须在 README 与 tasks 中强调顺序。

### 4. 目录布局约定（`soulking` 桶内）

| 前缀 | 用途 | 说明 |
|------|------|------|
| （根下分层路径） | 音频、歌词 `.lrc` | 现有 `object_key`，不变 |
| `avatar/` | 用户头像 | 不变 |
| `covers/` | 原 `music-covers` 桶对象 | 新前缀，供后续封面功能 |

### 5. 数据库

- `SongFile.object_key` 与 `User.avatar_object_key` **无需**因桶改名而更新（键不变）。
- 无 `music-covers` 相关列需迁移。

## Risks / Trade-offs

- **[Risk] 迁移中断导致双份或缺对象** → 脚本支持 dry-run、按桶统计对象数；复制完成后再删源；生产前备份 MinIO 数据目录。
- **[Risk] 部署与迁移顺序错误** → 文档与 tasks 明确「先迁移后改 env」；启动日志打印当前桶名。
- **[Risk] 旧 presigned URL 失效** → 可接受；用户刷新页面即可。
- **[Trade-off] 删除 `S3_BUCKET_COVERS`** → 若外部工具仍引用该变量需同步更新 `.env`。

## Migration Plan

1. 停止应用或进入维护窗口（可选，避免写入旧桶）。
2. 执行 `scripts/migrate_minio_to_soulking.py`（或等价 `mc mirror`）。
3. 更新 `.env`：`S3_BUCKET_MUSIC=soulking`，删除 `S3_BUCKET_COVERS`。
4. 部署/重启应用，确认 `ensure_buckets` 仅针对 `soulking`。
5. 抽样：流式播放、头像、`mc ls soulking/covers/`。
6. 确认后删除 `music-files`、`music-covers` 桶。

**回滚**：保留 MinIO 数据卷快照；若未删旧桶，可将 `S3_BUCKET_MUSIC` 指回 `music-files` 并回滚代码（不推荐长期双轨）。

## Open Questions

- 生产环境是否由运维手动执行 `mc` 而非仓库脚本——实现时在 README 注明推荐方式即可，不阻塞合并。
