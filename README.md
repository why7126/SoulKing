# Personal Music MVP

Python + FastAPI + SQLite + S3(MinIO) MVP for personal music management.

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

## 故障排除

- **`/admin` 连不上、进程启动失败**：请看终端日志。若为 `unable to open database file`，说明 SQLite 路径不可用。`.env` 里 `DATABASE_URL=sqlite:////data/music.db` **仅适合 Docker**（且需挂载 `./data:/data`）。在 **本机直接运行** `uvicorn` 时请改为 `DATABASE_URL=sqlite:///./data/music.db`（程序会自动创建父目录）。可先访问 `http://localhost:8000/health` 确认服务已起。
- **对象存储连接失败**：先确认 ProjectMinio 已启动且 `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9000/minio/health/live` 返回 `200`。Docker 运行应用时 `.env` 中应为 `S3_ENDPOINT_URL=http://host.docker.internal:9000`。应用启动时会 **最多约 90 秒** 内重试连接 MinIO（可先起容器再起 MinIO）；若仍失败，日志会提示先启动 ProjectMinio。本机直接 `uvicorn` 时用 `http://127.0.0.1:9000`。

## Notes

- 使用 Docker 时数据库在容器内路径 `/data/music.db`，对应宿主机 `./data/music.db`。
- 音频写入 **ProjectMinio** 中配置的桶（`S3_BUCKET_*`）；本仓库 compose 不包含 MinIO。
- This MVP is single-user and does not include auth.
