# Personal Music MVP

Python + FastAPI + SQLite + S3(MinIO) MVP for personal music management.

## Features

- Local directory scan and import to object storage
- Song aggregation with multi-format variants
- Song listing/search/filter
- Play selection with format priority
- Download by specific variant

## Quick Start

1. Copy env file:

```bash
cp .env.example .env
```

2. Put music files in `./import`.

3. Start services:

```bash
docker compose up --build
```

4. Open frontend:

`http://localhost:8000/`

5. Open API docs:

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

## Notes

- Database file is stored in `./data/music.db`.
- Imported files are uploaded to MinIO buckets.
- This MVP is single-user and does not include auth.
