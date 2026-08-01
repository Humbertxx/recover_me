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

## Current status

- Stage 2, decryption: ready via `scripts/01_decrypt.sh`.
- Stage 3, location: implemented in `src/locate.py`.
- Stage 4, Postbox access: **TODO** until the probe reports real format/schema
  evidence. No schema is assumed.
- Stage 5, extraction/rendering: **TODO** and intentionally not runnable until
  Stage 4 is understood.
