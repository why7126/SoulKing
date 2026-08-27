#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-local}"

exec bash deploy/scripts/down.sh "${DOMAIN}"
