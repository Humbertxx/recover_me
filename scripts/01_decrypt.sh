#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 1 ]]; then
  echo "Usage: $0 [backup-directory]" >&2
  exit 2
fi

project_root="$(cd "$(dirname "$0")/.." && pwd)"
output_path="$project_root/data/decrypted"

# Load local configuration when present.
if [[ -f "$project_root/.env" ]]; then
  set -a
  source "$project_root/.env"
  set +a
fi

backup_input="${1:-${FILE_TO_FOLDER:-}}"

if [[ -z "$backup_input" ]]; then
  echo "Set FILE_TO_FOLDER in .env or pass a backup directory." >&2
  exit 2
fi

if [[ ! -d "$backup_input" ]]; then
  echo "Backup directory does not exist: $backup_input" >&2
  exit 2
fi

backup_path="$(cd "$backup_input" && pwd)"

if [[ -z "${MVT_IOS_BACKUP_PASSWORD:-}" ]]; then
  echo "MVT_IOS_BACKUP_PASSWORD is not set." >&2
  exit 2
fi

mkdir -p "$output_path"
exec mvt-ios decrypt-backup -d "$output_path" "$backup_path"
