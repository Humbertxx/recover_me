"""Locate Telegram-related files in a decrypted iOS backup."""

import argparse
from pathlib import Path
import sqlite3

from .config import DECRYPTED_DIR


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=DECRYPTED_DIR)
    args = parser.parse_args()
    files = find_telegram_files(args.root)
    for path in files:
        print(path)
    print(f"Found {len(files)} Telegram-related file(s).")


def find_telegram_files(root: Path = DECRYPTED_DIR) -> list[Path]:
    """Return Telegram files mapped from an iOS backup manifest when available."""
    if not root.is_dir():
        raise FileNotFoundError(f"Decrypted backup directory does not exist: {root}")

    manifest = root / "Manifest.db"
    if manifest.is_file():
        return find_manifest_telegram_files(root, manifest)

    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and "telegra" in str(path).casefold()
    )


def find_manifest_telegram_files(root: Path, manifest: Path) -> list[Path]:
    """Map Telegram manifest records to MVT's decrypted hash-path layout."""
    database_uri = f"{manifest.as_uri()}?mode=ro"
    with sqlite3.connect(database_uri, uri=True) as connection:
        records = connection.execute(
            "SELECT fileID FROM Files "
            "WHERE lower(domain) LIKE '%telegra%' "
            "OR lower(relativePath) LIKE '%telegra%'"
        ).fetchall()

    files = [root / file_id[:2] / file_id for (file_id,) in records]
    return sorted(path for path in files if path.is_file())


if __name__ == "__main__":
    raise SystemExit(main())
