#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-local}"
ENVIRONMENT="${2:-sqlite-minio-external}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PROFILES=("docs-site")

case "${DOMAIN}:${ENVIRONMENT}" in
  local:sqlite-minio-external)
    COMPOSE_FILE="${ROOT_DIR}/deploy/local/compose.yml"
    ENV_FILE="${ROOT_DIR}/deploy/local/sqlite-minio-external.env"
    EXAMPLE_FILE="${ROOT_DIR}/deploy/local/sqlite-minio-external.env.example"
    ;;
  local:sqlite-minio-managed)
    COMPOSE_FILE="${ROOT_DIR}/deploy/local/compose.yml"
    ENV_FILE="${ROOT_DIR}/deploy/local/sqlite-minio-managed.env"
    EXAMPLE_FILE="${ROOT_DIR}/deploy/local/sqlite-minio-managed.env.example"
    PROFILES+=("self-hosted-storage")
    ;;
  prod:sqlite-minio-external)
    COMPOSE_FILE="${ROOT_DIR}/deploy/prod/compose.sqlite-minio-external.yml"
    ENV_FILE="${ROOT_DIR}/deploy/prod/sqlite-minio-external.env"
    EXAMPLE_FILE="${ROOT_DIR}/deploy/prod/sqlite-minio-external.env.example"
    ;;
  *)
    echo "Unsupported deploy environment: ${DOMAIN} ${ENVIRONMENT}" >&2
    exit 2
    ;;
esac

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "WARN: ${ENV_FILE} not found; using example file ${EXAMPLE_FILE}" >&2
  ENV_FILE="${EXAMPLE_FILE}"
fi

VALIDATE_ARGS=("--domain" "${DOMAIN}" "--environment" "${ENVIRONMENT}" "--env-file" "${ENV_FILE}")
COMPOSE_ARGS=("--project-name" "soulking" "--env-file" "${ENV_FILE}" "-f" "${COMPOSE_FILE}")
for profile in "${PROFILES[@]}"; do
  VALIDATE_ARGS+=("--profile" "${profile}")
  COMPOSE_ARGS+=("--profile" "${profile}")
done

python "${ROOT_DIR}/deploy/scripts/validate-env.py" "${VALIDATE_ARGS[@]}"

export SOULKING_DEPLOY_ENV_FILE="${ENV_FILE}"
docker compose "${COMPOSE_ARGS[@]}" up -d --build

HOST_PORT_APP="$(grep -E '^HOST_PORT_APP=' "${ENV_FILE}" | tail -1 | cut -d= -f2- || true)"
HOST_PORT_MINTLIFY_DOCS="$(grep -E '^HOST_PORT_MINTLIFY_DOCS=' "${ENV_FILE}" | tail -1 | cut -d= -f2- || true)"
echo "ProjectSoulKing app: http://localhost:${HOST_PORT_APP:-8000}"
echo "ProjectSoulKing API docs: http://localhost:${HOST_PORT_APP:-8000}/docs"
echo "ProjectSoulKing product manual preview: http://localhost:${HOST_PORT_MINTLIFY_DOCS:-3001}"
