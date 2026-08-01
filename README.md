# recover_me

Recover WhatsApp text conversations from an encrypted iPhone backup and render
them as a private, local HTML archive. The app reads the decrypted
`ChatStorage.sqlite` database and never changes the original backup.

## Setup

```sh
uv sync
```

Create `.env` from `.env.example`, then set the backup password and the path to
the iPhone backup's UDID directory. Keep the path quoted when it contains
spaces:

```sh
MVT_IOS_BACKUP_PASSWORD="your backup password"
FILE_TO_FOLDER="/path/to/MobileSync/Backup/<UDID>"
```

## Decrypt the backup

```sh
uv run ./scripts/01_decrypt.sh
```

The script loads `.env`, reads the backup in place, and writes the decrypted
files to `data/decrypted/`.

## Render WhatsApp conversations

List the private chat IDs and titles:

```sh
uv run python -m scripts.05_render_whatsapp --list-chats
```

Render one chat:

```sh
uv run python -m scripts.05_render_whatsapp --chat-id <ID>
```

Or render every chat and enable full sidebar navigation:

```sh
uv run python -m scripts.05_render_whatsapp --all-chats
```

The archive is written to `output/whatsapp/`. It uses local CSS and JavaScript
only—there is no runtime network dependency. Your messages render on the left;
other participants render on the right.

## View locally

```sh
uv run python -m http.server 8000 --directory output/whatsapp
```

Open `http://localhost:8000`, then press `Ctrl+C` to stop the server.

Edit `assets/conversation.css` to adjust the dark interface. Edit
`assets/conversation.js` to change the timestamp format used across every
conversation.
