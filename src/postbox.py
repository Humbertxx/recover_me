"""Narrow interface for Postbox database access.

TODO: Implement after scripts/02_probe.py provides real schema and encryption
evidence from the target backup. Telegram's Postbox is not assumed to be plain
SQLite.
"""

from pathlib import Path


def open_postbox(path: Path):
    """Return rows from a Postbox database (not yet implemented)."""
    raise NotImplementedError(
        "Postbox access requires probe evidence; run scripts/02_probe.py first "
        f"(candidate: {path})."
    )
