#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: scripts/archive-change.sh <change-id> [YYYY-MM-DD]" >&2
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

run_language_gate() {
  if [[ -f "scripts/validate-openspec-language.py" ]]; then
    python scripts/validate-openspec-language.py
  fi
}

run_openspec_archive() {
  local change="$1"
  local stdout_file
  local stderr_file
  stdout_file="$(mktemp)"
  stderr_file="$(mktemp)"

  if ! openspec archive "$change" -y >"$stdout_file" 2>"$stderr_file"; then
    cat "$stdout_file"
    cat "$stderr_file" >&2
    rm -f "$stdout_file" "$stderr_file"
    fail "openspec archive failed for $change"
  fi

  cat "$stdout_file"
  if grep -Eqi 'proposal\.md|Why|What Changes' "$stderr_file"; then
    if grep -Eqi 'Why|What Changes' "$stderr_file"; then
      echo "NOTE: OpenSpec CLI emitted an English scaffold heading compatibility warning. Project rule is Chinese-first; scripts/validate-openspec-language.py is the blocking gate." >&2
      grep -Evi 'proposal\.md|Why|What Changes' "$stderr_file" >&2 || true
    else
      cat "$stderr_file" >&2
    fi
  else
    cat "$stderr_file" >&2
  fi

  rm -f "$stdout_file" "$stderr_file"
}

relocate_legacy_archives() {
  local canonical_root="$1"
  local legacy_root="$2"

  if [[ ! -e "$legacy_root" ]]; then
    return 0
  fi
  if [[ ! -d "$legacy_root" ]]; then
    fail "$legacy_root exists but is not a directory"
  fi

  mkdir -p "$canonical_root"
  shopt -s nullglob dotglob

  local child
  for child in "$legacy_root"/*; do
    local target="$canonical_root/$(basename "$child")"
    if [[ -e "$target" ]]; then
      shopt -u nullglob dotglob
      fail "cannot migrate $child because $target already exists"
    fi
    mv "$child" "$target"
    echo "Migrated legacy archive: $child -> $target"
  done
  shopt -u nullglob dotglob

  rmdir "$legacy_root"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

change_id="${1:-}"
archive_date="${2:-$(date +%Y-%m-%d)}"

if [[ -z "$change_id" ]]; then
  usage
  exit 2
fi

if [[ ! "$archive_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  fail "archive date must use YYYY-MM-DD: $archive_date"
fi

project_root="$(pwd)"
canonical_root="$project_root/openspec/archive"
legacy_root="$project_root/openspec/changes/archive"
active_dir="$project_root/openspec/changes/$change_id"
target_dir="$canonical_root/$archive_date-$change_id"
legacy_target_dir="$legacy_root/$archive_date-$change_id"

[[ -d "$active_dir" ]] || fail "active change not found: openspec/changes/$change_id"
[[ ! -e "$target_dir" ]] || fail "archive target already exists: openspec/archive/$archive_date-$change_id"

run_language_gate
relocate_legacy_archives "$canonical_root" "$legacy_root"

mkdir -p "$canonical_root"
run_openspec_archive "$change_id"

if [[ -d "$legacy_target_dir" && ! -e "$target_dir" ]]; then
  mv "$legacy_target_dir" "$target_dir"
  echo "Relocated OpenSpec CLI legacy output to canonical archive: openspec/archive/$archive_date-$change_id"
fi

relocate_legacy_archives "$canonical_root" "$legacy_root"

[[ -d "$target_dir" ]] || fail "canonical archive target missing after archive: openspec/archive/$archive_date-$change_id"
[[ ! -e "$active_dir" ]] || fail "active change still exists after archive: openspec/changes/$change_id"

python scripts/validate-directory-structure.py
python scripts/validate-archive-evidence.py --change "$change_id" --archive-path "$target_dir"

echo "Archived OpenSpec change to openspec/archive/$archive_date-$change_id/"
