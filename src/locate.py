"""Locate Telegram-related files in a decrypted iOS backup."""

import argparse
from pathlib import Path

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
    """Return files whose path identifies them as Telegram application data."""
    if not root.is_dir():
        raise FileNotFoundError(f"Decrypted backup directory does not exist: {root}")
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and "telegra" in str(path).casefold()
    )


if __name__ == "__main__":
    raise SystemExit(main())
