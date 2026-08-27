#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-local}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

case "${DOMAIN}" in
  local)
    COMPOSE_FILE="${ROOT_DIR}/deploy/local/compose.yml"
    ;;
  prod)
    COMPOSE_FILE="${ROOT_DIR}/deploy/prod/compose.sqlite-minio-external.yml"
    ;;
  *)
    echo "Unsupported deploy domain: ${DOMAIN}" >&2
    exit 2
    ;;
esac

docker compose --project-name soulking --profile self-hosted-storage --profile docs-site -f "${COMPOSE_FILE}" down --remove-orphans
