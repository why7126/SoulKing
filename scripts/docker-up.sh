#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-local}"
ENVIRONMENT="${2:-sqlite-minio-external}"

exec bash deploy/scripts/up.sh "${DOMAIN}" "${ENVIRONMENT}"
