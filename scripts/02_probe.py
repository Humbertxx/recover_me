"""Inspect Telegram candidates without assuming that Postbox is SQLite.

Run from the repository root: ``uv run python -m scripts.02_probe``. Output
stays in the terminal and may contain private message data; never commit or
share it.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import quote

from src.config import DECRYPTED_DIR
from src.locate import find_telegram_files

SQLITE_MAGIC = b"SQLite format 3\x00"

def main():
    try:
        candidates = find_telegram_files(DECRYPTED_DIR)
    except FileNotFoundError as error:
        print(error)
        return 

    if not candidates:
        print("No Telegram-related files found. Run the locator and inspect the decrypted tree.")
        return 

    for path in candidates:
        relative_path = path.relative_to(DECRYPTED_DIR)
        print(f"\nCandidate: {relative_path} ({path.stat().st_size} bytes)")
        with path.open("rb") as file:
            header = file.read(32)
        print(f"  Header (hex): {header.hex()}")
        if header.startswith(SQLITE_MAGIC):
            probe_sqlite(path)
        else:
            print("  Not a plain SQLite database; no schema assumptions made.")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def probe_sqlite(path: Path) -> None:
    uri = f"file:{quote(path.as_posix())}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        tables = connection.execute(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        print(f"  SQLite tables: {len(tables)}")
        for name, schema in tables:
            print(f"\n  Table: {name}\n  Schema: {schema}")
            columns = connection.execute(
                f"PRAGMA table_info({quote_identifier(name)})"
            ).fetchall()
            print(f"  Columns: {columns}")
            samples = connection.execute(
                f"SELECT * FROM {quote_identifier(name)} LIMIT 3"
            ).fetchall()
            print(f"  Sample rows: {samples}")



if __name__ == "__main__":
    raise SystemExit(main())
