# Personal Music MVP

Python + FastAPI + SQLite + S3(MinIO) MVP for personal music management.

## Harness / AI 协作入口

本仓库已接入 ProjectSoulKing Harness 工程：

- AI 工作入口：[AGENTS.md](AGENTS.md)
- 项目事实源：[project.yaml](project.yaml)
- 长期文档索引：[docs/README.md](docs/README.md)
- 工程规则：[rules/](rules/)
- OpenSpec 项目说明：[openspec/project.md](openspec/project.md)
- Agent 技能入口：[.agents/skills/](.agents/skills/)

变更业务能力、接口契约、数据结构、权限边界、对象存储或部署拓扑时，应先创建 `openspec/changes/<change-id>/`，并按 `issues/`、`iterations/`、`openspec/` 的流程沉淀记录。

## Features

- Local directory scan and import to object storage（同内容 `sha256+file_size` 已存在则跳过；同歌名+同主艺人已有 `Song` 则只追加音频文件，不新建歌曲）
- 音频对象键：`music/{原唱1&原唱2}/{歌曲名}/{文件名}.{格式}`（路径段会清洗非法字符；全局唯一冲突时自动加 `_` + 哈希后缀）。保存歌曲元数据、`PATCH` 重命名文件、合并所选歌曲、批量更新后会按当前信息在桶内 **copy + 删旧键** 调整路径；后台 **音乐管理** 勾选歌曲后可用 **「同步存储路径」** 逐首调整（`POST /admin/songs/{song_id}/relocate-storage`，前端带进度条）
- Song aggregation with multi-format variants
- Song listing/search/filter
- Play selection with format priority
- Download by specific variant

## 重复歌曲合并（历史数据）

同一首曲目若因历史策略产生多条 `Song` 记录（相同标题、相同主 `artist_id`、时长在同一桶内且相差 ≤5 秒），启动时会自动合并一次（保留 **id 最小** 为主曲，其余文件的 `song_id` 与标签/语言/风格/艺人角色/歌单项并入主曲后删除从曲）。

- 迁移标记表 `_schema_migrations`，仅自动执行一次。
- 可手动再次执行：`POST /admin/merge-duplicate-songs`（无重复时 `merged_slave_songs` 为 0）。
- 后台 **音乐管理**：**「合并重复曲目」** 已从工具栏隐藏，需合并时可调 `POST /admin/merge-duplicate-songs`；**「合并所选歌曲」**（勾选 ≥2 首后显示，弹窗选择保留哪一条，接口 `POST /admin/songs/merge-selected`，body `{"song_ids":[...],"master_song_id": 目标歌曲 id}`）。
- **合并不删除音频与文件记录**：将各从曲的 `song_files` 仅改 `song_id` 到主曲，**全部保留**（含相同 sha256+file_size 但不同 `object_key` 的副本）。**「合并所选歌曲」不修改保留曲的元数据**（标签/语言/风格/艺人等不入主曲）；**启动时「合并重复曲目」** 仍会按历史规则合并元数据补全主曲。启动时会按需迁移以去掉历史上的 `(sha256, file_size)` 全局唯一约束。
- 后台 **编辑歌曲元数据** 为 **右侧抽屉**：每个音频文件一行展示信息与 **图标按钮**（悬停 `title` 为说明），支持 **试听**、**下载**、**重命名**（`PATCH /song-files/{id}` 改 `original_filename`，扩展名须与格式一致；保存后会 **按新歌名/文件名调整对象存储路径**）、**删除**（`DELETE /song-files/{id}` 删存储与记录）、**添加文件**（`POST /songs/{song_id}/files`，`multipart/form-data` 字段 `file`）。

## Quick Start

对象存储由并列目录 **ProjectMinio** 提供（独占本机 `9000` / 控制台 `9001`）。请先在其目录启动 MinIO，再启动本应用。

1. 启动全局 MinIO（一次即可常驻）：

```bash
cd ../ProjectMinio   # 与本仓库并列时
docker compose -f docker-compose.yaml -p minio up -d
```

2. Copy env file:

```bash
cp .env.example .env
```

3. Put music files in `./import`.

4. Start app：

```bash
docker compose up --build
```

5. Open frontend:

`http://localhost:8000/`

6. Open API docs:

`http://localhost:8000/docs`

## MVP API Flow

1. Trigger scan:

`POST /libraries/scan`

2. List songs:

`GET /songs`

3. Song detail with variants:

`GET /songs/{song_id}`

4. Get selected play variant:

`GET /songs/{song_id}/play`

5. Stream or download variant:

- `GET /song-files/{song_file_id}/stream`
- `GET /song-files/{song_file_id}/download`

## MinIO 单桶迁移（`music-files` / `music-covers` → `soulking`）

升级后应用仅使用一个桶（默认 `soulking`，环境变量 `S3_BUCKET_MUSIC`）。**必须先迁移对象，再改 `.env` 并重启应用**，否则播放与头像会 404。

1. 确认 ProjectMinio 已启动（`http://127.0.0.1:9000` 可访问）。
2. 在仓库根目录执行（本机跑脚本时用 `127.0.0.1`，脚本会自动把 `.env` 里的 `host.docker.internal` 换成 `127.0.0.1`）：

```bash
python scripts/migrate_minio_to_soulking.py --dry-run   # 预览
python scripts/migrate_minio_to_soulking.py             # 复制到 soulking 并校验对象数
python scripts/migrate_minio_to_soulking.py --delete-old-buckets   # 确认无误后删除旧桶
```

3. 将 `.env` 中 `S3_BUCKET_MUSIC=soulking`，删除已废弃的 `S3_BUCKET_COVERS`（若仍存在）。
4. 重启应用；`ensure_buckets` 仅确保 `soulking` 存在。

桶内布局：音频/歌词与头像键规则不变；原 `music-covers` 桶内对象位于 `covers/` 前缀下。

## 故障排除

- **`/admin` 连不上、进程启动失败**：请看终端日志。若为 `unable to open database file`，说明 SQLite 路径不可用。`.env` 里 `DATABASE_URL=sqlite:////data/music.db` **仅适合 Docker**（且需挂载 `./data:/data`）。在 **本机直接运行** `uvicorn` 时请改为 `DATABASE_URL=sqlite:///./data/music.db`（程序会自动创建父目录）。可先访问 `http://localhost:8000/health` 确认服务已起。
- **对象存储连接失败**：先确认 ProjectMinio 已启动且 `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9000/minio/health/live` 返回 `200`。Docker 运行应用时 `.env` 中应为 `S3_ENDPOINT_URL=http://host.docker.internal:9000`，并设置 `S3_PUBLIC_ENDPOINT_URL=http://127.0.0.1:9000`（供浏览器加载 presigned 头像/资源）。应用启动时会 **最多约 90 秒** 内重试连接 MinIO（可先起容器再起 MinIO）；若仍失败，日志会提示先启动 ProjectMinio。本机直接 `uvicorn` 时用 `http://127.0.0.1:9000`（可不设 `S3_PUBLIC_ENDPOINT_URL`）。
- **头像 Network 显示已拦截、URL 含 `host.docker.internal`**：浏览器无法稳定访问该主机名。在 `.env` 增加 `S3_PUBLIC_ENDPOINT_URL=http://127.0.0.1:9000` 后重启应用，再刷新页面。

## 用户登录与账号

- 除 `/login`、`POST /auth/login`、`GET /health` 与静态资源外，业务 API 须携带登录后的会话 Cookie。
- 首次**空库**启动时，根据 `.env` 中的 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 创建种子管理员（默认见 `.env.example`：`admin` / `Admin123!`）。密码须至少 8 位并含大小写、数字与特殊字符。
- 打开 `http://localhost:8000/login` 登录；前台侧栏可改个人资料与密码；管理员可进入 `/admin` 并在 **用户管理** 中创建其他账号（不开放自助注册）。
- 升级已有数据库时，历史歌单会归属种子管理员账号。

## Notes

- 使用 Docker 时数据库在容器内路径 `/data/music.db`，对应宿主机 `./data/music.db`。
- 音频与头像写入 **ProjectMinio** 的 `S3_BUCKET_MUSIC` 桶（默认 `soulking`）；本仓库 compose 不包含 MinIO。
- This MVP includes cookie-based auth and an admin console; it is still intended for private deployment.
