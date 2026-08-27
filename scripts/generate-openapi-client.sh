#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "${ROOT_DIR}/docs/generated"

(cd "${ROOT_DIR}" && python -c "import json; from app.main import app; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))") \
  > "${ROOT_DIR}/docs/generated/openapi.json"

echo "OpenAPI written to docs/generated/openapi.json"
