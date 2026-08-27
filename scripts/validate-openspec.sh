#!/usr/bin/env bash
set -euo pipefail
echo "Validate OpenSpec documents"

echo "校验目录结构..."
python scripts/validate-directory-structure.py

echo "校验 OpenSpec 文档中文优先..."
python scripts/validate-openspec-language.py
