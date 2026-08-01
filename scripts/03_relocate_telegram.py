#!/usr/bin/env python3
"""Copy backed-up Telegram files into their manifest-mapped paths.

The source backup is never modified. Files are copied from MVT's hashed
decrypted layout into ``data/extracted/telegram`` for straightforward review.
"""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import shutil
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "data" / "decrypted"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "extracted" / "telegram"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing extracted files",
    )
    args = parser.parse_args()

    manifest = args.source / "Manifest.db"
    if not manifest.is_file():
        parser.error(f"Manifest database does not exist: {manifest}")

    args.output.mkdir(parents=True, exist_ok=True)
    copied = skipped = missing = 0
    for file_id, domain, relative_path in telegram_records(manifest):
        source = args.source / file_id[:2] / file_id
        if not source.is_file():
            missing += 1
            continue

        destination = args.output / safe_relative_path(domain, relative_path, file_id)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and not args.overwrite:
            skipped += 1
            continue

        shutil.copy2(source, destination)
        copied += 1

    print(f"Copied: {copied}; existing skipped: {skipped}; missing source files: {missing}")
    print(f"Extracted Telegram files: {args.output}")
    return 0


def telegram_records(manifest: Path) -> list[tuple[str, str, str]]:
    database_uri = f"{manifest.as_uri()}?mode=ro"
    with sqlite3.connect(database_uri, uri=True) as connection:
        return connection.execute(
            "SELECT fileID, domain, relativePath FROM Files "
            "WHERE flags = 1 AND (lower(domain) LIKE '%telegra%' "
            "OR lower(relativePath) LIKE '%telegra%') "
            "ORDER BY domain, relativePath"
        ).fetchall()


def safe_relative_path(domain: str, relative_path: str, file_id: str) -> Path:
    path = PurePosixPath(relative_path or file_id)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe manifest path for {file_id}: {relative_path!r}")
    return Path(domain.replace("/", "_"), *path.parts)


if __name__ == "__main__":
    raise SystemExit(main())
