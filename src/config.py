"""Project paths and non-secret configuration."""

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BACKUP_DIR = DATA / "backup"
DECRYPTED_DIR = DATA / "decrypted"
EXTRACTED_DIR = DATA / "extracted"
OUTPUT_DIR = ROOT / "output"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
DESTINATION = OUTPUT_DIR / "index.html"
UDID = os.getenv("RECOVER_ME_UDID")
