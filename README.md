# recover_me

Inspect an encrypted iPhone backup, reconstruct its manifest-mapped files, and
render recovered WhatsApp text conversations as local HTML. Telegram discovery
is supported, but this backup does not contain its Postbox message database.

The decrypted backup and generated reports are private local artifacts and are
gitignored. The scripts only read from the original MobileSync backup and write
all derived data inside this repository. The backup password is read solely
from `MVT_IOS_BACKUP_PASSWORD`.

## Layout

- `data/backup/` — optional local backup copy
- `data/decrypted/` — output from `mvt-ios decrypt-backup`
- `data/extracted/` — manifest-mapped copies for inspection
- `output/` — generated local HTML archives
- `assets/` — local CSS and JavaScript copied into each archive

## Setup

```sh
uv sync
```

## Decrypt the backup

Set `FILE_TO_FOLDER` in `.env` to the UDID directory in your MobileSync backup.
Quote paths that contain spaces. The script loads `.env` automatically, reads
the original backup without modifying it, and writes decrypted files into
`data/decrypted/`:

```sh
MVT_IOS_BACKUP_PASSWORD="your backup password"
FILE_TO_FOLDER="/path/to/MobileSync/Backup/<UDID>"
```

```sh
uv run ./scripts/01_decrypt.sh
```

You can also pass a backup directory directly:

```sh
uv run ./scripts/01_decrypt.sh /path/to/backup/<UDID>
```

The script invokes:

```sh
mvt-ios decrypt-backup -d data/decrypted/ <backup-directory>
```

The final argument is the supplied backup directory; it does not have to be
inside `data/backup/`.

## Inspect recovered files

Locate Telegram files through the iOS manifest. Decrypted backup filenames are
hash IDs, so this command maps them back to their Telegram records:

```sh
uv run python -m src.locate
```

Probe the mapped Telegram files without printing private file contents:

```sh
uv run python -m scripts.02_probe
```

Copy the backed-up Telegram files into their original manifest paths for
inspection. This never changes the source backup or decrypted files:

```sh
uv run python scripts/03_relocate_telegram.py
```

To reconstruct the complete decrypted backup into its original domain and path
layout, run the full extractor. It copies all ordinary files, recreates empty
directories, and writes `manifest-index.tsv`; it does not change the decrypted
backup. This duplicates the data, so first preview its size with `--dry-run`:

```sh
uv run python scripts/04_relocate_backup.py --dry-run
uv run python scripts/04_relocate_backup.py
```

## Render a WhatsApp conversation

List chat IDs and titles (the output is private):

```sh
uv run python -m scripts.05_render_whatsapp --list-chats
```

Render one selected chat as local HTML:

```sh
uv run python -m scripts.05_render_whatsapp --chat-id <ID>
```

To generate every chat page and enable navigation from the desktop sidebar:

```sh
uv run python -m scripts.05_render_whatsapp --all-chats
```

The page is written to `output/whatsapp/index.html` with text messages ordered
by their WhatsApp timestamps. The dark chat UI deliberately places **your**
messages on the left and other participants on the right. It reads
`ChatStorage.sqlite` directly from the decrypted backup and does not change
that database. A single-chat render shows the full sidebar but only the active
chat is available; use `--all-chats` to make every sidebar item navigable.

The archive uses only local `conversation.css` and `conversation.js` files;
there is no Tailwind CDN or other runtime network dependency.

Serve the rendered archive locally:

```sh
uv run python -m http.server 8000 --directory output/whatsapp
```

Open `http://localhost:8000` in a browser, then press `Ctrl+C` in the terminal
to stop the server. Edit `assets/conversation.js` to change date/time formatting
for every rendered conversation, and edit `assets/conversation.css` for the
dark chat theme. The default visible date format is `2021-09-23 23:30:21`,
with no `+00:00` suffix.

## Current status

- Backup decryption and manifest-based file reconstruction: ready.
- Telegram discovery: ready; Postbox extraction remains unavailable without a
  Postbox database in the backup.
- WhatsApp text conversation rendering: ready.
