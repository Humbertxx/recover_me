#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 data/backup/<UDID>" >&2
  exit 2
fi

project_root="$(cd "$(dirname "$0")/.." && pwd)"
backup_root="$project_root/data/backup"
output_path="$project_root/data/decrypted"

if [[ ! -d "$1" ]]; then
  echo "Backup directory does not exist: $1" >&2
  exit 2
fi

backup_path="$(cd "$1" && pwd)"

if [[ "$backup_path" != "$backup_root"/* ]]; then
  echo "Refusing to decrypt a backup outside $backup_root" >&2
  echo "Copy the original backup into data/backup/ first." >&2
  exit 2
fi

if [[ -z "${MVT_IOS_BACKUP_PASSWORD:-}" ]]; then
  echo "MVT_IOS_BACKUP_PASSWORD is not set." >&2
  exit 2
fi

mkdir -p "$output_path"
exec mvt-ios decrypt-backup -d "$output_path" "$backup_path"
