"""Extract text conversations from a WhatsApp iOS ChatStorage database."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

from .config import DECRYPTED_DIR
from .models import Chat, ChatSummary, Contact, Message


APPLE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)
WHATSAPP_DOMAIN = "AppDomainGroup-group.net.whatsapp.WhatsApp.shared"
WHATSAPP_CHAT_STORAGE = "ChatStorage.sqlite"


def find_chat_storage(root: Path = DECRYPTED_DIR) -> Path:
    """Return the decrypted ChatStorage database mapped by Manifest.db."""
    manifest = root / "Manifest.db"
    if not manifest.is_file():
        raise FileNotFoundError(f"Manifest database does not exist: {manifest}")

    database_uri = f"{manifest.as_uri()}?mode=ro"
    with sqlite3.connect(database_uri, uri=True) as connection:
        row = connection.execute(
            "SELECT fileID FROM Files "
            "WHERE domain = ? AND relativePath = ? AND flags = 1",
            (WHATSAPP_DOMAIN, WHATSAPP_CHAT_STORAGE),
        ).fetchone()
    if row is None:
        raise FileNotFoundError("WhatsApp ChatStorage.sqlite is not present in this backup")

    file_id = row[0]
    database = root / file_id[:2] / file_id
    if not database.is_file():
        raise FileNotFoundError(f"Decrypted WhatsApp database does not exist: {database}")
    return database


def list_chats(database: Path) -> list[ChatSummary]:
    """Return the available WhatsApp chats for navigation or selection."""
    with read_only_connection(database) as connection:
        rows = connection.execute(
            "SELECT Z_PK, "
            "COALESCE(NULLIF(ZPARTNERNAME, ''), NULLIF(ZCONTACTIDENTIFIER, ''), "
            "NULLIF(ZCONTACTJID, ''), 'Chat ' || Z_PK), "
            "ZMESSAGECOUNTER "
            "FROM ZWACHATSESSION "
            "WHERE COALESCE(ZREMOVED, 0) = 0 "
            "ORDER BY ZLASTMESSAGEDATE DESC, Z_PK"
        ).fetchall()
    return [
        ChatSummary(id=int(chat_id), title=str(title), message_count=int(message_count or 0))
        for chat_id, title, message_count in rows
    ]


def extract_chat(database: Path, chat_id: int) -> Chat:
    """Extract text messages for one WhatsApp chat session."""
    with read_only_connection(database) as connection:
        chat_row = connection.execute(
            "SELECT Z_PK, "
            "COALESCE(NULLIF(ZPARTNERNAME, ''), NULLIF(ZCONTACTIDENTIFIER, ''), "
            "NULLIF(ZCONTACTJID, ''), 'Chat ' || Z_PK) "
            "FROM ZWACHATSESSION WHERE Z_PK = ?",
            (chat_id,),
        ).fetchone()
        if chat_row is None:
            raise ValueError(f"WhatsApp chat ID {chat_id} was not found")

        message_rows = connection.execute(
            "SELECT m.Z_PK, m.ZTEXT, m.ZMESSAGEDATE, m.ZSENTDATE, m.ZISFROMME, "
            "m.ZFROMJID, m.ZPUSHNAME, gm.ZCONTACTNAME, gm.ZFIRSTNAME, pp.ZPUSHNAME "
            "FROM ZWAMESSAGE AS m "
            "LEFT JOIN ZWAGROUPMEMBER AS gm ON gm.Z_PK = m.ZGROUPMEMBER "
            "LEFT JOIN ZWAPROFILEPUSHNAME AS pp ON pp.ZJID = m.ZFROMJID "
            "WHERE m.ZCHATSESSION = ? "
            "AND m.ZTEXT IS NOT NULL AND trim(m.ZTEXT) != '' "
            "ORDER BY COALESCE(m.ZMESSAGEDATE, m.ZSENTDATE), m.ZSORT, m.Z_PK",
            (chat_id,),
        ).fetchall()

    messages = [
        Message(
            id=message_id,
            chat_id=chat_id,
            text=text,
            date=apple_timestamp(message_date if message_date is not None else sent_date),
            sender=message_sender(
                is_from_me,
                from_jid,
                message_push_name,
                group_contact_name,
                group_first_name,
                profile_push_name,
            ),
            is_from_me=bool(is_from_me),
        )
        for (
            message_id,
            text,
            message_date,
            sent_date,
            is_from_me,
            from_jid,
            message_push_name,
            group_contact_name,
            group_first_name,
            profile_push_name,
        ) in message_rows
    ]
    return Chat(id=int(chat_row[0]), title=str(chat_row[1]), messages=messages)


def read_only_connection(database: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{database.resolve().as_uri()}?mode=ro", uri=True)


def apple_timestamp(value: float | int | None) -> datetime | None:
    if value is None:
        return None
    return APPLE_EPOCH + timedelta(seconds=float(value))


def message_sender(
    is_from_me: int | None,
    from_jid: str | None,
    message_push_name: str | None,
    group_contact_name: str | None,
    group_first_name: str | None,
    profile_push_name: str | None,
) -> Contact:
    if is_from_me:
        return Contact(id="me", name="You")
    name = next(
        (
            value
            for value in (
                group_contact_name,
                group_first_name,
                profile_push_name,
                message_push_name,
                from_jid,
            )
            if value
        ),
        "Unknown sender",
    )
    return Contact(id=from_jid or name, name=name)
