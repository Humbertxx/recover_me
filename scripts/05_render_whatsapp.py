#!/usr/bin/env python3
"""List WhatsApp chats or render one chat's text messages as local HTML."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config import OUTPUT_DIR
from src.render import render_chats
from src.whatsapp import extract_chat, find_chat_storage, list_chats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-chats", action="store_true", help="list available chat IDs")
    parser.add_argument("--chat-id", type=int, help="WhatsApp chat ID to render")
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR / "whatsapp",
        help="directory for the HTML archive",
    )
    args = parser.parse_args()
    if args.list_chats == (args.chat_id is not None):
        parser.error("choose exactly one of --list-chats or --chat-id")

    database = find_chat_storage()
    if args.list_chats:
        for chat_id, title, message_count in list_chats(database):
            print(f"{chat_id}\t{message_count}\t{title}")
        return 0

    chat = extract_chat(database, args.chat_id)
    index_path = render_chats([chat], args.output)
    print(f"Rendered {len(chat.messages)} text message(s): {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
