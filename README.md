# recover_me

Recover Telegram conversation history from an encrypted iPhone backup and
render it as browsable HTML.

The decrypted backup and generated reports are private local artifacts and are
gitignored. Never modify the original MobileSync backup; work only from a copy
inside `data/backup/`. The backup password is read solely from
`MVT_IOS_BACKUP_PASSWORD`.

## Layout

- `data/backup/` — raw MobileSync backup copy
- `data/decrypted/` — output from `mvt-ios decrypt-backup`
- `data/extracted/` — extracted Postbox database files
- `output/` — generated HTML reports

## Setup

```sh
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Run stages 1–3

Set `FILE_TO_FOLDER` in `.env` to the UDID directory in your MobileSync backup.
The script reads the original backup without modifying it and writes decrypted
files into `data/decrypted/`:

```sh
uv run ./scripts/01_decrypt.sh
```

You can also pass a backup directory directly:

```sh
uv run ./scripts/01_decrypt.sh /path/to/backup/<UDID>
```

The script invokes:

```sh
mvt-ios decrypt-backup -d data/decrypted/ data/backup/<UDID>
```

Locate Telegram files:

```sh
uv run python -m src.locate
```

Probe the files before implementing Postbox access or extraction:

```sh
uv run python -m scripts.02_probe
```

Copy the backed-up Telegram files into their original manifest paths for
inspection. This never changes the source backup or decrypted files:

```sh
uv run python scripts/03_relocate_telegram.py
```

To reconstruct the complete decrypted backup into its original domain and path
layout, run the full extractor. This duplicates the decrypted data, so first
preview its size with `--dry-run`:

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

The page is written to `output/whatsapp/index.html` with text messages ordered
by their WhatsApp timestamps. It reads `ChatStorage.sqlite` directly from the
decrypted backup and does not change that database.

Serve the rendered archive locally:

```sh
uv run python -m http.server 8000 --directory output/whatsapp
```

Open `http://localhost:8000` in a browser, then press `Ctrl+C` in the terminal
to stop the server. Edit `assets/conversation.js` to change date/time formatting
for every rendered conversation. The default visible format is
`2021-09-23 23:30:21`, with no `+00:00` suffix.

## Current status

- Stage 2, decryption: ready via `scripts/01_decrypt.sh`.
- Stage 3, location: implemented in `src/locate.py`.
- Stage 4, Postbox access: **TODO** until the probe reports real format/schema
  evidence. No schema is assumed.
- Stage 5, Telegram extraction/rendering: **TODO** until Postbox is understood.
- WhatsApp text conversation rendering: ready.
