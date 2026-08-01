"""List WhatsApp chats or render one chat's text messages as local HTML."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config import OUTPUT_DIR
from src.render import render_chats
from src.whatsapp import extract_chat, find_chat_storage, list_chats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list-chats", action="store_true", help="list available chat IDs")
    mode.add_argument("--chat-id", type=int, help="WhatsApp chat ID to render")
    mode.add_argument(
        "--all-chats",
        action="store_true",
        help="render every available chat and enable sidebar navigation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR / "whatsapp",
        help="directory for the HTML archive",
    )
    args = parser.parse_args()
    database = find_chat_storage()
    if args.list_chats:
        for chat in list_chats(database):
            print(f"{chat.id}\t{chat.message_count}\t{chat.title}")
        return 0

    sidebar_chats = list_chats(database)
    if args.all_chats:
        chats = [extract_chat(database, int(chat.id)) for chat in sidebar_chats]
        index_path = render_chats(
            chats,
            args.output,
            sidebar_chats=sidebar_chats,
            navigation_enabled=True,
        )
        print(f"Rendered {len(chats)} conversation(s): {index_path}")
        return 0

    chat = extract_chat(database, args.chat_id)
    index_path = render_chats([chat], args.output, sidebar_chats=sidebar_chats)
    print(f"Rendered {len(chat.messages)} text message(s): {index_path}")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
